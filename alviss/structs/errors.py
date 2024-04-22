__all__ = [
    'AlvissError',
    'AlvissStubberError',
    'AlvissStubberSyntaxError',
    'AlvissStubberInvalidTypeName',
]


class AlvissError(Exception):
    pass


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
