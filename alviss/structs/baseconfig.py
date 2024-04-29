__all__ = [
    "BaseConfig",
]
from ccptools.structs import *
from ccptools.tpu import iters
from ccptools.tpu import string
import json
import yaml
import collections
from alviss.utils import *


class _KwSafeEmptyDict(EmptyDict):
    def __getattribute__(self, name):
        name = unescape_keyword(name)
        if hasattr(collections.defaultdict, name):
            return collections.defaultdict.__getattribute__(self, name)
        if collections.defaultdict.__contains__(self, name):
            data = collections.defaultdict.__getitem__(self, name)
            if isinstance(data, dict):
                return _KwSafeEmptyDict(**data)
            elif data is None:
                return Empty
            else:
                return data
        return Empty

    def __getitem__(self, item):
        item = unescape_keyword(item)
        if collections.defaultdict.__contains__(self, item):
            data = collections.defaultdict.__getitem__(self, item)
            if isinstance(data, dict):
                return _KwSafeEmptyDict(**data)
            elif data is None:
                return Empty
            else:
                return data
        return Empty


class BaseConfig(object):
    """This object simplifies accessing configuration values by more-or-less
    behaving like a `ccptools.structs.EmptyDict`.

    That is to say, just access any value, no matter how nested it is, via dot
    attributes. If any part of the requested value wasn't in the loaded
    configuration file, the resulting value will just be an `Empty` (from
    `ccptools.structs.Empty`).

    Given the following `example.yaml` config file:
    ```yaml
    plugins:
        foo_plug:
            enabled: true
            foo_config: bar or something
    ```

    Loading this with Alviss as a BaseConfig object will result in the following:
    ```python
    >>> from alviss import quickloader
    >>> cfg = quickloader.autoload('example.yaml')
    >>> print(cfg.plugins.foo_plug.enabled)
    True
    >>> print(cfg.plugins.foo_plug.foo_config)
    bar or something
    >>> print(cfg.plugins.bar_plug.enabled)
    ```


    """
    _secret_keys = {'pass', 'secret', 'token', 'key'}

    def __init__(self, **kwargs):
        super().__setattr__('_data', _KwSafeEmptyDict(**kwargs))

    def __getattr__(self, item):
        return _KwSafeEmptyDict.__getattribute__(self._data, item)

    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        self.update(**{key: value})

    def __str__(self):
        return _KwSafeEmptyDict.__str__(self._repr_dump(self._data))  # noqa

    def __repr__(self):
        return _KwSafeEmptyDict.__repr__(self._repr_dump(self._data))  # noqa

    def as_json(self, unmaksed: bool = False) -> str:
        return json.dumps(self.as_dict(unmaksed=unmaksed), indent=4)

    def as_yaml(self, unmaksed: bool = False) -> str:
        return yaml.dump(self.as_dict(unmaksed=unmaksed))

    def as_dict(self, unmaksed: bool = False) -> dict:
        return self._data if unmaksed else self._repr_dump(self._data)

    @classmethod
    def _repr_dump(cls, cfg_map: dict):
        d = {}
        for k, v in cfg_map.items():
            if isinstance(v, dict):
                d[k] = cls._repr_dump(v)
            elif isinstance(v, (str, bytes)) and cls._is_key_secret(k):
                d[k] = '********'
            else:
                d[k] = v
        return d

    @classmethod
    def _is_key_secret(cls, key: str):
        key = string.str_norm(key)
        for sk in cls._secret_keys:
            if sk in key:
                return True
        return False

    def load(self, **kwargs):
        super().__setattr__('_data', _KwSafeEmptyDict(**kwargs))

    def update(self, **kwargs):
        iters.nested_dict_update(self._data, _KwSafeEmptyDict(**kwargs))

