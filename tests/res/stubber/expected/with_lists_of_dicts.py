from typing import *
from alviss.structs import Empty
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


class _CfgFooBarListOfPeopleHealthStub(_BaseCfgStub, dict):
    blood_pressure: Union[int, Empty]
    weight: Union[float, Empty]
    alive: Union[bool, Empty]


class _CfgFooBarListOfPeopleStub(_BaseCfgStub, dict):
    name: Union[str, Empty]
    age: Union[int, Empty]
    shoe_size: Union[float, Empty]
    favorite_foods: Union[List[str], Empty]
    health: Union[_CfgFooBarListOfPeopleHealthStub, Empty]


class _CfgFooBarListOfImportantPeopleStub(_BaseCfgStub, dict):
    name: str
    title: Union[str, Empty]


class _CfgFooBarStub(_BaseCfgStub, dict):
    list_of_people: Union[List[_CfgFooBarListOfPeopleStub], Empty]
    list_of_important_people: List[_CfgFooBarListOfImportantPeopleStub]


class _CfgFooStub(_BaseCfgStub, dict):
    bar: _CfgFooBarStub


class _CfgStub(_BaseCfgStub, dict):
    foo: _CfgFooStub
