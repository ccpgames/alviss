__all__ = [
    'CfgImportTestSkillsStub',
    'CfgImportTestInventoryStub',
    'CfgImportTestStub',
    'CfgHereBeStufPeopleStub',
    'CfgHereBeStufMandatoryPeopleStub',
    'CfgHereBeStufStub',
    'CfgStub',
    'ConfigStub',
]

from ccptools.structs import *
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


class CfgImportTestSkillsStub(_BaseCfgStub):
    level: Union[int, Empty]
    group: str


class CfgImportTestInventoryStub(_BaseCfgStub):
    weight: Union[float, Empty]
    quantity: Union[int, Empty]


class CfgImportTestStub(_BaseCfgStub):
    other_list: Union[List[Union[str, float]], Empty]
    required_list: List[str]
    skills: Dict[str, CfgImportTestSkillsStub]
    inventory: Union[Dict[str, CfgImportTestInventoryStub], Empty]


class CfgHereBeStufPeopleStub(_BaseCfgStub):
    name: str
    age: Union[int, Empty]
    favorite_color: Union[str, Empty]


class CfgHereBeStufMandatoryPeopleStub(_BaseCfgStub):
    name: str
    age: Union[int, Empty]
    level: int


class CfgHereBeStufStub(_BaseCfgStub):
    people: List[CfgHereBeStufPeopleStub]
    mandatory_people: List[CfgHereBeStufMandatoryPeopleStub]
    sub_seven: Dict[str, Any]


class CfgStub(_BaseCfgStub):
    my_list: Union[List[str], Empty]
    my_required_list: List[str]
    myDifferentList: Union[List[str], Empty]
    myDifferentRequiredList: List[Union[str, int]]
    myDifferentRequiredListByKeyName: List[Any]
    import_test: CfgImportTestStub
    here_be_stuf: CfgHereBeStufStub


class ConfigStub(BaseConfig, CfgStub):
    pass
