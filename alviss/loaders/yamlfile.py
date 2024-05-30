__all__ = [
    'YamlFileConfigLoader',
]

from .base import *
import yaml

import logging
log = logging.getLogger(__name__)


class YamlFileConfigLoader(BaseLoader):
    def load_raw(self, raw_data: str, no_resolve: bool = False,
                 no_extend: bool = False, no_includes: bool = False, no_env_load: bool = False,
                 no_fidelius: bool = False, no_py_inject: bool = False):
        self._skip_resolve = no_resolve
        self._skip_env_loading = no_env_load
        self._skip_includes = no_includes
        self._skip_extends = no_extend
        self._skip_fidelius = no_fidelius
        self._skip_py_inject = no_py_inject
        self._data = self._load_dict(yaml.safe_load(raw_data))
        self._set_chains()
        if not no_extend:
            self._extend()
        if not no_includes:
            self._includes()
        if not no_resolve:
            self._resolve()
        if not no_fidelius:
            self._fetch_fidelius()

    @property
    def rendered(self) -> str:
        return yaml.dump(self._data)
