__all__ = [
    'CfgLoggingRootStub',
    'CfgLoggingFormattersBaseStub',
    'CfgLoggingFormattersStub',
    'CfgLoggingHandlersStub',
    'CfgLoggingLoggersStub',
    'CfgLoggingStub',
    'CfgStub',
    'AlvissConfigStub',
]

from typing import *
from alviss.structs import Empty
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


class CfgLoggingRootStub(_BaseCfgStub, dict):
    level: Union[str, Empty]
    handlers: Union[List[str], Empty]


class CfgLoggingFormattersBaseStub(_BaseCfgStub, dict):
    format: Union[str, Empty]


class CfgLoggingFormattersStub(_BaseCfgStub, dict):
    base: Union[CfgLoggingFormattersBaseStub, Empty]


class CfgLoggingHandlersStub(_BaseCfgStub, dict):
    level: Union[str, Empty]
    class_: Union[str, Empty]
    formatter: Union[str, Empty]


class CfgLoggingLoggersStub(_BaseCfgStub, dict):
    handlers: Union[List[str], Empty]
    level: Union[str, Empty]
    propagate: Union[bool, Empty]


class CfgLoggingStub(_BaseCfgStub, dict):
    version: Union[int, Empty]
    disable_existing_loggers: Union[bool, Empty]
    root: Union[CfgLoggingRootStub, Empty]
    formatters: Union[CfgLoggingFormattersStub, Empty]
    handlers: Union[Dict[str, CfgLoggingHandlersStub], Empty]
    loggers: Union[Dict[str, CfgLoggingLoggersStub], Empty]


class CfgStub(_BaseCfgStub, dict):
    logging: Union[CfgLoggingStub, Empty]


class AlvissConfigStub(BaseConfig, CfgStub):
    pass
