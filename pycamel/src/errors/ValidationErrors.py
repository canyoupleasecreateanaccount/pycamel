class AbsentValidationItems(Exception):
    """ Raise when nothing has been passed to validator as validation target """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.passed_value = kwargs.get('passed_value')


class IncorrectAssertParameter(Exception):
    """
    Raise when incorrect type of filter has been passed to .validate method
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.passed_value = kwargs.get('passed_value')
