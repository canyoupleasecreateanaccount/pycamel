class ForbiddenParameter(Exception):
    """
    Raise when forbidden parameter has been passed into function.
    """
    def __init__(self, *args):
        super().__init__(*args)


class RequestException(Exception):
    """
    Raise when request throw an exeption during execution.
    """
    def __init__(self, *args):
        super().__init__(*args)
