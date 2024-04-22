__all__ = [
    'SimpleStubMaker',
]
from alviss.quickloader import autoload
from .interface import *
from ._structs import *
from alviss.structs.errors import *

import os
import pathlib

import logging
log = logging.getLogger(__file__)


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

    def render_stub_classes_to_file(self, input_file: str, output_file: str, overwrite_existing: bool = False):
        out = pathlib.Path(output_file).absolute()
        if out.exists() and not overwrite_existing:
            raise AlvissFileAlreadyExistsError('Output file already exists', file_name=output_file)

        results = self.render_stub_classes_from_descriptor_file(input_file)

        if not out.parent.exists():
            log.debug(f'Creating output path: {out.parent}')
            os.makedirs(out.parent, exist_ok=True)

        with open(output_file, 'w') as fin:
            fin.write(results)

        return
