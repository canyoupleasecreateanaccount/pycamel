class AbsentValidationItems(Exception):
    """ Raise when nothing has been passed to validator as validation target """
    def __init__(self, *args):
        super().__init__(*args)


class IncorrectAssertParameter(Exception):
    """
    Raise when incorrect type of filter has been passed to .validate method
    """
    def __init__(self, *args):
        super().__init__(*args)


class IncorrectValidationPath(Exception):
    """
    Raise when path to validation item is not correct.
    """
    def __init__(self, *args):
        super().__init__(*args)
