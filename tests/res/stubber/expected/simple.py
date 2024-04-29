__all__ = [
    'AlvissConfigStub',
]

from typing import *
from alviss.structs import Empty
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


class _CfgInternalRefDeeperStub(_BaseCfgStub, dict):
    there: Union[str, Empty]
    everywhere: str


class _CfgInternalRefStub(_BaseCfgStub, dict):
    deeper: _CfgInternalRefDeeperStub


class _CfgGroupStub(_BaseCfgStub, dict):
    alpha: Union[str, int, Empty]
    beta: Union[float, int, str]
    gamma_with_var: Union[str, None, Empty]
    delta: Union[int, None, Empty]


class _CfgCollapsedGroupInOneStub(_BaseCfgStub, dict):
    string: Union[int, Empty]


class _CfgCollapsedGroupInStub(_BaseCfgStub, dict):
    one: Union[_CfgCollapsedGroupInOneStub, Empty]


class _CfgCollapsedGroupStub(_BaseCfgStub, dict):
    successful: Union[bool, Empty]
    in_: Union[_CfgCollapsedGroupInStub, Empty]


class _CfgCollapsedStub(_BaseCfgStub, dict):
    other_group: Union[Dict[str, Any], None, Empty]
    group: Union[_CfgCollapsedGroupStub, Empty]


class _CfgImportTestStub(_BaseCfgStub, dict):
    imported_keys: Union[Dict[str, str], Empty]


class _CfgShouldBeSevenStub(_BaseCfgStub, dict):
    sub_seven: Dict[str, Any]


class _CfgStub(_BaseCfgStub, dict):
    foo: Union[str, Empty]
    internal_ref: _CfgInternalRefStub
    base_key: Union[int, Empty]
    foo_inherited: Union[float, Empty]
    bar: float
    group: _CfgGroupStub
    collapsed: Union[_CfgCollapsedStub, Empty]
    my_list: Union[List[str], Empty]
    import_test: Union[_CfgImportTestStub, Empty]
    should_be_seven: _CfgShouldBeSevenStub


class AlvissConfigStub(BaseConfig, _CfgStub):
    pass
