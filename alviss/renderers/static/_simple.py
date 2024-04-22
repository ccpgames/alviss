__all__ = [
    'SimpleStaticRenderer',
]

from .interface import *
from alviss import quickloader
from alviss.structs.errors import *

import os
import pathlib

import logging
log = logging.getLogger(__file__)


class SimpleStaticRenderer(IStaticRenderer):
    def render_static_config_from_file(self, file: str) -> str:
        return quickloader.render_load(file)

    def render_static_config_to_file(self, input_file: str, output_file: str, overwrite_existing: bool = False):
        out = pathlib.Path(output_file).absolute()
        if out.exists() and not overwrite_existing:
            raise AlvissFileAlreadyExistsError('Output file already exists', file_name=output_file)

        results = self.render_static_config_from_file(input_file)

        if not out.parent.exists():
            log.debug(f'Creating output path: {out.parent}')
            os.makedirs(out.parent, exist_ok=True)

        with open(output_file, 'w') as fin:
            fin.write(results)

        return
