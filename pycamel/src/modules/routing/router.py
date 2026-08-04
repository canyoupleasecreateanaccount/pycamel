from typing import Any, Callable

import contextlib
import copy
import os
import threading

import requests
from urllib3.util.retry import Retry

from pycamel.src.modules.core.config import CamelConfig
from pycamel.src.modules.core.filter import Filter
from pycamel.src.modules.response.response import CamelResponse

from pycamel.src.errors.SystemErrors import ForbiddenParameter, RequestException

RETRY_STATUS_FORCELIST = [502, 503, 504]


class Router:
    """
    Default router class that gives possibility to send requests as it
    implemented in base requests lib, but with some additionally functionality.
    """
    def __init__(
            self,
            path: str,
            *,
            router_validation_key: str = None,
            default_headers: dict = None,
            timeout: float = None,
            retries: int = None,
            backoff_factor: float = None,
            auth_provider: Callable[[], dict] = None
    ) -> None:
        """
        :param path: Concreate router path. For example /users
        :param router_validation_key: Key that will be used for each request
        :param default_headers: Dict. Default is None. Dict with headers
            that will be used as default headers.
        and type of request under that route for .validate method.
        :param timeout: Default timeout (in seconds) applied to every request
            sent from this router, unless a request explicitly passes its own
            timeout=. Default is None, meaning no timeout is enforced, unless
            one has been configured on CamelConfig.
        :param retries: Number of retries for requests that fail with one of
            RETRY_STATUS_FORCELIST status codes. Default is None, meaning the
            value configured on CamelConfig is used, falling back to 0
            (no retries) when nothing has been configured.
        :param backoff_factor: Backoff factor applied between retries.
            Default is None, meaning the value configured on CamelConfig is
            used, falling back to 0.5 when nothing has been configured.
        :param auth_provider: A zero-argument callable that returns a dict of
            headers, called again before every request sent from this
            router, so it naturally supports token refresh. Default is None,
            meaning the auth_provider configured on CamelConfig is used, if
            any. Headers returned by it can still be overridden per request
            with .append_header/.set_headers.

        A single Router instance builds one request at a time in its own
        instance state (request_path/request_headers), from the first
        builder call (.add_to_path/.set_headers/.set_filters/.append_header)
        through the terminal .get/.post/.put/.patch/.delete call that sends
        it and clears that state back to defaults. If the same Router is
        shared across threads, that build-then-send sequence ("chain") is
        automatically serialized per thread, so one thread's in-progress
        request can never be corrupted by another thread's builder calls;
        a second thread's chain simply blocks until the first one's request
        has been sent.
        """
        self.path = path
        self.router_validation_key = router_validation_key
        self.headers = self._update_default_headers(default_headers)

        self.request_path = path
        self.request_headers = copy.deepcopy(self.headers)

        self.timeout = timeout if timeout is not None \
            else self._env_float('pc_default_timeout')
        self.retries = retries if retries is not None \
            else self._env_int('pc_retries', default=0)
        self.backoff_factor = backoff_factor if backoff_factor is not None \
            else self._env_float('pc_backoff_factor', default=0.5)
        self.auth_provider = auth_provider if auth_provider is not None \
            else CamelConfig.get_auth_provider()

        self.session = self._build_session(self.retries, self.backoff_factor)

        self._execution_method = None
        self._chain_lock = threading.Lock()
        self._chain_owner = None

    @staticmethod
    def _env_float(key: str, default: float = None) -> float:
        """
        Reads env variable and converts it to float, returns default value
        if variable is absent.
        """
        value = os.environ.get(key)
        return float(value) if value is not None else default

    @staticmethod
    def _env_int(key: str, default: int = None) -> int:
        """
        Reads env variable and converts it to int, returns default value
        if variable is absent.
        """
        value = os.environ.get(key)
        return int(value) if value is not None else default

    @staticmethod
    def _build_session(retries: int, backoff_factor: float) -> requests.Session:
        """
        Builds a requests.Session for the router, reused across requests for
        connection pooling. Mounts a retry-enabled adapter when retries > 0.
        :param retries: Number of retries for RETRY_STATUS_FORCELIST codes.
        :param backoff_factor: Backoff factor applied between retries.
        :return: requests.Session instance.
        """
        session = requests.Session()
        if retries:
            retry = Retry(
                total=retries,
                backoff_factor=backoff_factor,
                status_forcelist=RETRY_STATUS_FORCELIST
            )
            adapter = requests.adapters.HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
        return session

    @staticmethod
    def _update_default_headers(headers: dict = None):
        """
        Method updates default headers according to received dict of headers.

        :param headers: Dict. Default is None. Dict with headers that will be
               used as default headers.
        :return: Dict with updated headers.
        """
        updated_headers = {'Content-Type': 'application/json'}
        if headers:
            for key in headers.keys():
                updated_headers[key] = headers[key]
        return updated_headers

    def _begin_chain(self) -> bool:
        """
        Ensures the calling thread owns this router's request-building
        chain (add_to_path/set_headers/set_filters/append_header through
        the terminal get/post/put/patch/delete call), blocking until
        another thread's in-flight chain has completed and been cleared.
        :return: True when this call is the one that acquired the lock
            (and is therefore responsible for releasing it on error via
            _end_chain), False when the calling thread already owned it.
        """
        current_thread = threading.get_ident()
        if self._chain_owner == current_thread:
            return False
        # Deliberately not a `with` block: this lock is acquired here and
        # released later, potentially from a different call
        # (_end_chain/_clear), once the whole builder-to-fetch chain
        # completes - not at the end of this method.
        self._chain_lock.acquire()  # pylint: disable=consider-using-with
        self._chain_owner = current_thread
        return True

    def _end_chain(self) -> None:
        """
        Releases ownership of the router's request-building chain, if the
        calling thread currently owns it, allowing another thread's chain
        to proceed. Safe to call even when nothing is owned.
        :return: None
        """
        if self._chain_owner == threading.get_ident():
            self._chain_owner = None
            self._chain_lock.release()

    @contextlib.contextmanager
    def _chain_guard(self):
        """
        Context manager for the builder methods: acquires chain ownership
        if not already held by the calling thread, and releases it again
        if the wrapped mutation raises, so a failed builder call never
        leaves the chain permanently locked. On success, ownership is
        intentionally kept until the terminal get/post/put/patch/delete
        call (or a direct ._clear()) releases it.
        """
        acquired = self._begin_chain()
        try:
            yield
        except Exception:
            if acquired:
                self._end_chain()
            raise

    def _clear(self) -> None:
        """
        Method updates router object to default after each fetched request,
        and releases the request-building chain if the calling thread
        holds it, so another thread's builder calls can proceed.
        :return: Nothing
        """
        self.request_path = self.path
        self.request_headers = copy.deepcopy(self.headers)
        self._end_chain()

    def _fetch(self, *args, **kwargs) -> CamelResponse:
        """
        Method receives any default values from requests lib and push them into
        execution method. After request execution it returns CamelResponse.
        :param args: Not supported, kept only to surface a clear error.
        :param kwargs: Any
        :return: CamelResponse
        """
        try:
            if args:
                raise ForbiddenParameter(
                    "Positional arguments are not supported by API methods, "
                    "please use keyword arguments instead, for example "
                    "params=, json=, data=, timeout=."
                )
            if "headers" in kwargs or "url" in kwargs:
                raise ForbiddenParameter(
                    "Parameters url and headers could be passed from API "
                    "method, they could be set only by set methods."
                )
            if self.timeout is not None:
                kwargs.setdefault('timeout', self.timeout)
            request_headers = self.request_headers
            try:
                if self.auth_provider is not None:
                    request_headers = {
                        **self.auth_provider(), **self.request_headers
                    }
                response = self._execution_method(
                    url=self.request_path,
                    headers=request_headers,
                    **kwargs
                )
            except Exception as ex:
                raise RequestException(
                    f"During request execution we faced with error, please "
                    f"take a look: \n {ex}") from ex
            return CamelResponse(
                response=response,
                headers=copy.deepcopy(request_headers),
                router_validation_key=self.router_validation_key,
                request_data=kwargs.get('data'),
                request_json=kwargs.get('json')
            )
        finally:
            self._clear()

    def get(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Not supported, raises ForbiddenParameter if passed.
        :param kwargs: Optional arguments that ``request`` takes.
               Except url and header
        :return: Result of execution _fetch method. CamelResponse class.
        """
        self._begin_chain()
        self._execution_method = self.session.get
        return self._fetch(*args, **kwargs)

    def post(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Not supported, raises ForbiddenParameter if passed.
        :param kwargs: Optional arguments that ``request`` takes.
               Except url and header
        :return: Result of execution _fetch method. CamelResponse class.
        """
        self._begin_chain()
        self._execution_method = self.session.post
        return self._fetch(*args, **kwargs)

    def put(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Not supported, raises ForbiddenParameter if passed.
        :param kwargs: Optional arguments that ``request`` takes.
               Except url and header
        :return: Result of execution _fetch method. CamelResponse class.
        """
        self._begin_chain()
        self._execution_method = self.session.put
        return self._fetch(*args, **kwargs)

    def patch(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Not supported, raises ForbiddenParameter if passed.
        :param kwargs: Optional arguments that ``request`` takes.
               Except url and header
        :return: Result of execution _fetch method. CamelResponse class.
        """
        self._begin_chain()
        self._execution_method = self.session.patch
        return self._fetch(*args, **kwargs)

    def delete(self, *args, **kwargs) -> CamelResponse:
        """
        Request method based on :class:`Request` of requests lib.
        Gets request method as object and makes request.
        :param args: Not supported, raises ForbiddenParameter if passed.
        :param kwargs: Optional arguments that ``request`` takes.
               Except url and header
        :return: Result of execution _fetch method. CamelResponse class.
        """
        self._begin_chain()
        self._execution_method = self.session.delete
        return self._fetch(*args, **kwargs)

    def add_to_path(self, parameter: str) -> 'Router':
        """
        Method adds to request path any received string.
        For example, if you need to send request to localhost/api/users/12
        all that you have to do it just .add_to_path('/12').
        :param parameter: Any string.
        :return: returns self
        """
        with self._chain_guard():
            self.request_path += parameter
        return self

    def set_headers(self, headers: dict) -> 'Router':
        """
        Method switch default application/json header to received dict with
        headers.
        :param headers: dictionary with needed headers.
        :return: returns self
        """
        with self._chain_guard():
            self.request_headers = headers
        return self

    def set_filters(self, filters: dict) -> 'Router':
        """
        Method receives dictionary with needed filters, transform it into string
        and add to request url. For example: base url is localhost/api/users,
        and you set filters {"page": 1}, for now your request url will be
        localhost/api/users?page=1
        :param filters: dictionary with filters
        :return: returns self
        """
        with self._chain_guard():
            self.request_path += Filter.build_filter(filters)
        return self

    def append_header(self, header_key: str, header_value: Any) -> 'Router':
        """
        Method appends to default headers, received key and value.
        For example: default header is {'Content-Type': 'application/json'},
        after append header key-APP, value-TEST, it will look like
        {'Content-Type': 'application/json', 'APP': 'TEST'}.
        :param header_key: any string value
        :param header_value: any value
        :return: returns self
        """
        with self._chain_guard():
            self.request_headers[header_key] = header_value
        return self
