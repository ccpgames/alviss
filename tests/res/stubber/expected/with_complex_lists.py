__all__ = [
    'CfgFooStub',
    'CfgFoolStub',
    'CfgBarYomamaStub',
    'CfgBarStub',
    'CfgStub',
]

from typing import *
from alviss.structs import Empty
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


class CfgFooStub(_BaseCfgStub, dict):
    my_list: Union[List[str], Empty]
    my_required_list: List[str]


class CfgFoolStub(_BaseCfgStub, dict):
    myDifferentList: Union[List[str], Empty]
    myDifferentMultiTypeList: Union[List[Union[str, float]], Empty]


class CfgBarYomamaStub(_BaseCfgStub, dict):
    myDifferentRequiredList: List[Union[str, int]]
    myDifferentRequiredListByKeyName: List[Any]


class CfgBarStub(_BaseCfgStub, dict):
    yomama: CfgBarYomamaStub


class CfgStub(_BaseCfgStub, dict):
    Foo: CfgFooStub
    fool: Union[CfgFoolStub, Empty]
    bar: CfgBarStub
