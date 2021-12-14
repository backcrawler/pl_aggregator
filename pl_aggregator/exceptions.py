class ResponceCodeError(Exception):
    '''Errors with invalid response code'''

    def __init__(self, code: int):
        self.code = code
