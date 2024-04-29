__all__ = [
    'is_keyword',
    'escape_keyword',
    'unescape_keyword',
]


_KW_FIELDS = {  # These can't be field names in dataclasses
    'False',
    'None',
    'True',
    'and',
    'as',
    'assert',
    'async',
    'await',
    'break',
    'class',
    'continue',
    'def',
    'del',
    'elif',
    'else',
    'except',
    'finally',
    'for',
    'from',
    'global',
    'if',
    'import',
    'in',
    'is',
    'lambda',
    'nonlocal',
    'not',
    'or',
    'pass',
    'raise',
    'return',
    'try',
    'while',
    'with',
    'yield',
}


def is_keyword(string: str, include_escaped: bool = False) -> bool:
    """Given a string, returns True if it is a Python keyword (and thus can't
    be used as a field name in a dataclass).

    :param string: The string to check
    :param include_escaped: Also checks if the given string is an escaped
                            keyword (keyword with an appended underscore). False
                            by default.
    :return: True if the string is a Python keyword')
    """
    if include_escaped and string[-1] == '_':
        string = string[:-1]
    return string in _KW_FIELDS


def escape_keyword(string: str) -> str:
    """Returns an escaped version of the given string, if it is a Python
    keyword. Escaping just involves adding an appended underscore to its name.

    :param string: The string to escape
    :return: The string with an appended underscore, if it was a Python keyword,
             but otherwise the same string, unaltered.
    """
    if is_keyword(string):
        return f'{string}_'
    return string


def unescape_keyword(string: str) -> str:
    """If the given string is an escaped Python keyword (i.e. a keyword with an
    appended underscore) removes the underscore and returns that keyword.
    Otherwise the given string is returned unaltered.

    :param string: The string to unescape
    :return: The string with its underscore removed, if it was an escaped Python
             keyword
    """
    if string[-1] != '_':
        return string  # Doesn't need unescaping!
    check_string = string[:-1]
    if is_keyword(check_string):
        return check_string
    return string
