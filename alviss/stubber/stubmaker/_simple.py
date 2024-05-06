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
    def render_stub_classes_from_descriptor_file(self, file, is_private: bool = True,
                                                 class_name: str = 'AlvissConfigStub') -> str:
        cfg = autoload(file)
        root_stub = StubClass.from_dict(cfg.as_dict(unmaksed=True), is_private=is_private)
        res = []
        class_names = []
        for stub in root_stub.get_all_sub_stubs():
            if not stub.class_name.startswith('_'):
                class_names.append(stub.class_name)
            res.append(stub.render_class_str())
        if not root_stub.class_name.startswith('_'):
            class_names.append(root_stub.class_name)
        res.append(root_stub.render_class_str())
        class_str = '\n\n\n'.join(res)

        if class_name:
            class_names.append(class_name)

        all_str = ''
        if class_names:
            all_str = '\n'.join([f"    '{c}'," for c in class_names])
            all_str = f"""__all__ = [
{all_str}
]

"""
        root_cls = ''
        if class_name:
            root_cls = f"""


class {class_name}(BaseConfig, {root_stub.class_name}):
    pass"""

        return f"""{all_str}from typing import *
from alviss.structs import Empty
from alviss.structs.cfgstub import _BaseCfgStub
from alviss.structs import BaseConfig


{class_str}{root_cls}"""

    def render_stub_classes_to_file(self, input_file: str, output_file: str, overwrite_existing: bool = False, is_private: bool = True, class_name: str = 'AlvissConfigStub'):
        out = pathlib.Path(output_file).absolute()
        if out.exists() and not overwrite_existing:
            raise AlvissFileAlreadyExistsError('Output file already exists', file_name=output_file)

        results = self.render_stub_classes_from_descriptor_file(input_file, is_private=is_private, class_name=class_name)

        if not out.parent.exists():
            log.debug(f'Creating output path: {out.parent}')
            os.makedirs(out.parent, exist_ok=True)

        with open(output_file, 'w') as fin:
            fin.write(results)
            fin.write('\n')

        return
