__all__ = [
    'autoload',
    'guess_loader_class',
    'raw_load',
    'render_load',
]

import os

from alviss.structs import *
from .interface import *
from .jsonfile import *
from .yamlfile import *

_EXTENSION_LOADER_MAP = {
    '.json': JsonFileConfigLoader,
    '.yaml': YamlFileConfigLoader,
    '.yml': YamlFileConfigLoader,
}


def guess_loader_class(file_name: str) -> Type[IAlvissLoader]:
    """Returns the most probable loader class based of the given file's extension.
    """
    ext = os.path.splitext(file_name)[-1]
    loader = _EXTENSION_LOADER_MAP.get(ext, None)
    if not loader:
        raise AlvissUnknownFileTypeError(f'Dont know how to autoload file extension {ext}', file_name=file_name)
    return loader


def raw_load(file_name: str, skip_env_loading: bool = False, skip_fidelius: bool = False, skip_py_inject: bool = False, encoding: str = 'utf-8') -> Dict:
    """Loads and parses the given config file and returns the "raw" results as a
    simple python dictionary.

    This is mostly intended for the testing and debugging of the configuration
    files themselves if needed.

    :param file_name: The file to load
    :param skip_env_loading: Set to True to skip resolving environment variable tags
    :param skip_fidelius: Set to True to skip resolving Fidelius tags
    :param skip_py_inject: Set to True to skip injecting Python imported values
    :param encoding: Encoding to use when reading the file (utf-8 by default)
    :return: A dict with the results
    """
    loader = guess_loader_class(file_name)()
    loader.load_file(file_name, no_env_load=skip_env_loading, no_fidelius=skip_fidelius,
                     no_py_inject=skip_py_inject, encoding=encoding)
    return loader.data


def render_load(file_name: str, skip_env_loading: bool = True, skip_fidelius: bool = True, skip_py_inject: bool = True, encoding: str = 'utf-8') -> str:
    """Loads and parses the given config file and returns the "render" results
    as a str in the same format the original file used.

    The main point of this method is to be able to load and parse an Alviss
    configuration file, including all includes, extensions, internal references,
    environment variables, Fidelius values etc. and render as a single
    value/file of the same format.

    As a use-case example, it was originally built in order to generate
    Kubernetes YAML manifest files using Alviss' format to simplify the process
    (i.e. includes, internal references, secret injection via Fidelius during
    deployment and so on).

    :param file_name: The file to load
    :param skip_env_loading: Set to True to skip resolving environment variable
                             tags
    :param skip_fidelius: Set to True to skip resolving Fidelius tags
    :param skip_py_inject: Set to True to skip injecting Python imported values
    :param encoding: Encoding to use when reading the file (utf-8 by default)
    :return: A string representation of the configuration data loaded, in the
             same format as the target file if possible
    """
    loader = guess_loader_class(file_name)()
    loader.load_file(file_name, no_env_load=skip_env_loading, no_fidelius=skip_fidelius, no_py_inject=skip_py_inject, encoding=encoding)
    return loader.rendered


def autoload(file_name: str, encoding: str = 'utf-8') -> BaseConfig:
    """Loads and parses the given config file and returns as a `BaseConfig`
    object.

    :param file_name:
    :type file_name:
    :param encoding:
    :type encoding:
    :return:
    :rtype:
    """
    loader = guess_loader_class(file_name)()
    loader.load_file(file_name, encoding=encoding)
    return BaseConfig(**raw_load(file_name))
