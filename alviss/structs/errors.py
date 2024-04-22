__all__ = [
    'AlvissError',
    'AlvissFileNotFoundError',
    'AlvissFileAlreadyExistsError',
    'AlvissParsingError',

    'AlvissSyntaxError',
    'AlvissExpressionResolvingError',
    'AlvissFideliusError',
    'AlvissFideliusNotInstalledError',
    'AlvissFideliusSyntaxError',

    'AlvissUnknownFileTypeError',
    'AlvissStubberError',
    'AlvissStubberSyntaxError',
    'AlvissStubberInvalidTypeName',
]


class AlvissError(Exception):
    pass


class AlvissFileNotFoundError(AlvissError, FileNotFoundError):
    def __init__(self, message: str, file_name: str = '?'):
        super().__init__(message)
        self.file_name = file_name

    def __str__(self):
        return f'{super().__str__()} (file_name="{self.file_name}")'


class AlvissFileAlreadyExistsError(AlvissError, FileExistsError):
    def __init__(self, message: str, file_name: str = '?'):
        super().__init__(message)
        self.file_name = file_name

    def __str__(self):
        return f'{super().__str__()} (file_name="{self.file_name}")'


class AlvissParsingError(AlvissError, ValueError):
    pass


class AlvissSyntaxError(AlvissParsingError):
    pass


class AlvissExpressionResolvingError(AlvissParsingError):
    pass


class AlvissFideliusError(AlvissExpressionResolvingError):
    pass


class AlvissFideliusNotInstalledError(AlvissExpressionResolvingError, ImportError):
    pass


class AlvissFideliusSyntaxError(AlvissExpressionResolvingError, AlvissSyntaxError):
    pass


class AlvissUnknownFileTypeError(AlvissParsingError, NotImplementedError):
    def __init__(self, message: str, file_name: str = '?'):
        super().__init__(message)
        self.file_name = file_name

    def __str__(self):
        return f'{super().__str__()} (file_name="{self.file_name}")'


class AlvissStubberError(AlvissError):
    pass


class AlvissStubberSyntaxError(AlvissStubberError, ValueError):
    def __init__(self, message: str, field_name: str = '?'):
        super().__init__(message)
        self.field_name = field_name

    def __str__(self):
        return f'{super().__str__()} (field_name="{self.field_name}")'


class AlvissStubberInvalidTypeName(AlvissStubberSyntaxError, TypeError):
    def __init__(self, message: str, field_name: str = '?', type_name: str = '?'):
        super().__init__(message, field_name)
        self.type_name = type_name

    def __str__(self):
        return f'{super().__str__()} (type_name="{self.type_name}", field_name="{self.field_name}")'
