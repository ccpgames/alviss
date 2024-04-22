import re

from ccptools.structs import *


PATTERN = re.compile(r'(\w+)')


def _loop_over_type_words(string: str) -> str:
    new_s = []
    i = 0
    print(string)
    string = string.replace(' ', '')
    for match in PATTERN.finditer(string):
        if match.start() > i:
            new_s.append(string[i:match.start()])
        word = string[match.start():match.end()]

        # Process word!
        new_s.append(word.upper())


        i = match.end()
    if len(string) >= i:
        new_s.append(string[i:])
    print(new_s)
    ss = ''.join(new_s)
    return ss.replace(',', ', ')


if __name__ == '__main__':
    string = '  Dict[str,   Dict[str,str], str] '
    print(string)
    print(_loop_over_type_words(string))
