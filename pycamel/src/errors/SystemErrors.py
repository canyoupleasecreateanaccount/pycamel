class ForbiddenParameter(Exception):
    """
    Raise when forbidden parameter has been passed into function.
    """
    def __init__(self, *args):
        """Constructor, forwards all args to the base Exception class."""
        super().__init__(*args)


class RequestException(Exception):
    """
    Raise when request throw an exeption during execution.
    """
    def __init__(self, *args):
        """Constructor, forwards all args to the base Exception class."""
        super().__init__(*args)


class MissingConfigError(Exception):
    """
    Raise when a route is built before CamelConfig has been initiated
    with a host.
    """
    def __init__(self, *args):
        """Constructor, forwards all args to the base Exception class."""
        super().__init__(*args)
