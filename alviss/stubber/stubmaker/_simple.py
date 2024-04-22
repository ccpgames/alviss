__all__ = [
    'SimpleStubMaker',
]
from alviss.quickloader import autoload
from .interface import *
from ._structs import *


class SimpleStubMaker(IStubMaker):
    def render_stub_classes_from_descriptor_file(self, file) -> str:
        cfg = autoload(file)
        root_stub = StubClass.from_dict(cfg.as_dict(unmaksed=True))
        res = []
        class_names = []
        for stub in root_stub.get_all_sub_stubs():
            class_names.append(stub.class_name)
            res.append(stub.render_class_str())
        class_names.append(root_stub.class_name)
        res.append(root_stub.render_class_str())
        class_str = '\n\n\n'.join(res)

        all_str = '\n'.join([f"    '{c}'," for c in class_names])

        return f"""__all__ = [
{all_str}
    'AlvissConfigStub',  
]

from typing import *
from alviss.structs import Empty
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


{class_str}


class AlvissConfigStub(BaseConfig, CfgStub):
    pass"""

