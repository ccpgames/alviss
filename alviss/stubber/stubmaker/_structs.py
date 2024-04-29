__all__ = [
    'StubField',
    'StubClass',
]
import dataclasses
from typing import *
from alviss.structs.errors import *
from alviss.utils import *
import re

import logging
log = logging.getLogger(__name__)


_WORD_PATTERN = re.compile(r'(\w+)')

_VALID_TYPE_NAME_SET = {
    'str',
    'int',
    'float',
    'bool',

    'None',
    'Empty',
    'Dict',
    'List',
    'Any',
    'Union'
}

_CAP_WORD_SET = {
    'none',
    'empty',
    'dict',
    'list',
    'any',
    'union',
}


@dataclasses.dataclass
class StubField:
    name: str
    value: Union[str, List[str], 'StubClass']
    is_self_required: bool
    ancestors: List[str] = dataclasses.field(default_factory=list)
    is_dict_list: bool = False
    is_map_of_stuff: bool = False

    def __post_init__(self):
        self._fix_and_validate_type_names()

    def _fix_type_name(self, type_name: str, has_bracket: bool = False) -> str:
        og_type_name = type_name
        type_name = type_name.strip().lower()
        if type_name in _CAP_WORD_SET:
            type_name = type_name.capitalize()
        if type_name not in _VALID_TYPE_NAME_SET:
            raise AlvissStubberInvalidTypeName(f'Invalid type name', field_name=self.name, type_name=og_type_name)

        if type_name == 'Dict' and not has_bracket:
            type_name = 'Dict[str,Any]'  # Default
        elif type_name == 'List' and not has_bracket:
            type_name = 'List[Any]'
        return type_name

    def _loop_over_type_words(self, string: str) -> str:
        new_s = []
        i = 0
        string = string.replace(' ', '')
        for match in _WORD_PATTERN.finditer(string):
            if match.start() > i:
                new_s.append(string[i:match.start()])
            word = string[match.start():match.end()]
            has_bracket = string[match.end():match.end()+1] == '['
            new_s.append(self._fix_type_name(word, has_bracket))
            i = match.end()
        if len(string) >= i:
            new_s.append(string[i:])
        return ''.join(new_s).replace(',', ', ')

    def _fix_and_validate_type_names(self):
        if isinstance(self.value, StubClass):
            return
        elif isinstance(self.value, list):
            new_list = []
            for v in self.value:
                new_list.append(self._loop_over_type_words(v))
            self.value = new_list
        else:
            self.value = self._loop_over_type_words(self.value)

    @property
    def safe_field_name(self) -> str:
        return escape_keyword(self.name)

    @property
    def is_required(self) -> bool:
        return self.is_self_required or self.has_required_children

    @property
    def has_required_children(self) -> bool:
        if isinstance(self.value, StubClass):
            return self.value.has_required_fields
        return False

    @classmethod
    def from_keyval(cls, key: str, value: Union[str, List, Dict], ancestors: Optional[List[str]],
                    is_map_of_stuff: bool = False,
                    pre_required: bool = False,
                    is_private: bool = True) -> 'StubField':
        required = pre_required

        if key.endswith('*'):
            required = True
            key = key[:-1].strip()

        if isinstance(value, dict):
            if len(value) == 1 and ('${str}' in value or '${str}*' in value):
                sub_key, sub_val = value.popitem()
                if sub_key.endswith('*'):
                    required = True
                return cls.from_keyval(key=key, value=sub_val, pre_required=required,
                                       ancestors=ancestors, is_map_of_stuff=True, is_private=is_private)

            else:
                value = StubClass.from_dict(input_dict_or_list=value, field_name=key, ancestors=ancestors, is_private=is_private)
                return cls(name=key, value=value, is_self_required=required,
                           ancestors=ancestors, is_map_of_stuff=is_map_of_stuff)

        elif isinstance(value, list):
            if len(value) != 1:
                raise AlvissStubberSyntaxError('Lists in type descriptor files must have exactly one element',
                                               field_name='.'.join(ancestors+[key]))

            if isinstance(value[0], dict):
                value = StubClass.from_dict(input_dict_or_list=value[0], field_name=key, ancestors=ancestors, is_private=is_private)
                return cls(name=key, value=value, is_self_required=required, ancestors=ancestors,
                           is_dict_list=True, is_map_of_stuff=is_map_of_stuff)

            elif isinstance(value[0], str):
                value = value[0].strip()

                if value.endswith('*'):
                    required = True
                    value = value[:-1]

                if '|' in value:  # Todo: this does not handle brackets, e.g. List[str|int]
                    value_list = [p.strip() for p in value.split('|')]
                    value = f'Union[{",".join(value_list)}]'
                value = f'List[{value}]'

                # Then continue below as if it's a string!

            else:
                raise AlvissStubberSyntaxError(f'Unexpected type in list of descriptor file: {type(value[0])}',
                                               field_name='.'.join(ancestors+[key]))
        elif isinstance(value, str):
            if value.endswith('*'):
                required = True
                value = value[:-1].strip()
            if '|' in value:  # Todo: this does not handle brackets, e.g. List[str|int]
                value = [p.strip() for p in value.split('|')]

        return cls(name=key, value=value, is_self_required=required, ancestors=ancestors.copy(),
                   is_map_of_stuff=is_map_of_stuff)

    def render_field_str(self) -> str:
        if isinstance(self.value, StubClass):
            if self.is_required:
                if self.is_dict_list:
                    return f'    {self.safe_field_name}: List[{self.value.class_name}]'
                elif self.is_map_of_stuff:
                    return f'    {self.safe_field_name}: Dict[str, {self.value.class_name}]'
                else:
                    return f'    {self.safe_field_name}: {self.value.class_name}'
            else:
                if self.is_dict_list:
                    type_list = [f'List[{self.value.class_name}]', 'Empty']
                elif self.is_map_of_stuff:
                    type_list = [f'Dict[str, {self.value.class_name}]', 'Empty']
                else:
                    type_list = [self.value.class_name, 'Empty']

        elif isinstance(self.value, list):
            type_list = self.value
            if not self.is_required:
                type_list.append('Empty')
        else:
            if self.is_required:
                return f'    {self.safe_field_name}: {self.value}'
            else:
                type_list = [self.value, 'Empty']

        return f'    {self.safe_field_name}: Union[{", ".join(type_list)}]'


@dataclasses.dataclass
class StubClass:
    name: str
    ancestors: List[str] = dataclasses.field(default_factory=list)
    fields: List[StubField] = dataclasses.field(default_factory=list)
    is_private: bool = True

    @property
    def has_required_fields(self) -> bool:
        for field in self.fields:
            if field.is_required:
                return True
        return False

    @classmethod
    def from_dict(cls,
                  input_dict_or_list: Union[Dict[str, Any], List[Any]],
                  field_name: str = '',
                  ancestors: Optional[List[str]] = None,
                  is_private: bool = True) -> 'StubClass':
        ancestors = ancestors or []
        ancestors.append(field_name)
        if isinstance(input_dict_or_list, dict):
            fields = [StubField.from_keyval(k, v, ancestors.copy(), is_private=is_private) for k, v in input_dict_or_list.items()]
        elif isinstance(input_dict_or_list, list):  # Should you ever get a list...?!?
            log.warning('NOT SURE THIS SHOULD EVER HAPPEN!!!')
            fields = [StubField.from_keyval('__list__', input_dict_or_list[0], ancestors.copy(), is_private=is_private)]
        else:
            raise AlvissStubberSyntaxError(f'Unexpected type fed to StubClass.from_dict: {type(input_dict_or_list)}')
        ancestors.pop()
        return cls(name=field_name, ancestors=ancestors, fields=fields, is_private=is_private)

    @staticmethod
    def field_name_to_class_name(field_name: str) -> str:
        if not field_name.isupper() and not field_name.islower():  # Mixed Casing
            tmp = []
            for c in field_name:
                if c.isupper():
                    if not tmp:
                        tmp.append(c)
                    else:
                        tmp.append('_')
                        tmp.append(c)
                else:
                    tmp.append(c)
            field_name = ''.join(tmp)
        parts = field_name.split('_')
        buff = []
        for part in parts:
            if not part:
                continue
            buff.append(part.capitalize())
        result = ''.join(buff)
        return escape_keyword(result)  # Just in case!

    @property
    def class_name(self) -> str:
        start = 'Cfg'
        if self.is_private:
            start = '_Cfg'
        if not self.name:
            return f'{start}Stub'
        else:
            if self.ancestors:
                return f'{start}{"".join([self.field_name_to_class_name(a) for a in self.ancestors+[self.name]])}Stub'
            else:
                return f'{start}{self.field_name_to_class_name(self.name)}Stub'

    def render_class_str(self) -> str:
        lines = [f'class {self.class_name}(_BaseCfgStub, dict):']
        for field in self.fields:
            lines.append(field.render_field_str())
        return '\n'.join(lines)

    def get_all_sub_stubs(self) -> List['StubClass']:
        lst = []
        for field in self.fields:
            if isinstance(field.value, StubClass):
                lst.extend(field.value.get_all_sub_stubs())
                lst.append(field.value)
        return lst


if __name__ == '__main__':
    d = StubClass.from_dict({
        'foo': 'int*',
        'bar': 'str|int',
        'sub_shit': {
            'extra': {
                'foo': 'str',
                'bar': 'str|bool*',
            },
            'bar': 'float',
        }
    })
    for s in d.get_all_sub_stubs():
        print(s.render_class_str())
        print('----------')
    print(d.render_class_str())