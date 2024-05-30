__all__ = [
    'BaseLoader',
]

from alviss.structs import *
from .interface import *
from ccptools.tpu import iters
from ccptools.tpu import strimp
import os
import logging
log = logging.getLogger(__file__)


_VAR_PATTERN = re.compile(r'\$\{(?P<var>(?:[^=}\s]+)(?:!?=[^}]*)?)}')


class BaseLoader(IAlvissLoader, abc.ABC):
    def __init__(self):
        self._file_name = ''
        self._file_path = ''
        self._data: Dict = {}

        self._unresolved: Dict[Sequence[str], str] = {}
        self._extends: List[Sequence[str, Sequence[str]]] = []
        self._include: List[Sequence[str, Sequence[str]]] = []
        self._chains: List[Tuple[Sequence[str], str]] = []

        self._resolve_count = 0
        self._special_key_map: Dict[str, Callable] = {
            '__extends__': self._special_key_extends,
            '__extend__': self._special_key_extends,
            '__include__': self._special_key_include,
            '__includes__': self._special_key_include,
            '__fidelius__': self._special_key_fidelius,
        }

        self._skip_resolve: bool = False
        self._skip_env_loading: bool = False
        self._skip_includes: bool = False
        self._skip_extends: bool = False
        self._skip_fidelius: bool = False
        self._skip_py_inject: bool = False

        self._fidelius_keys: Dict[Sequence[str], str] = {}
        self._fidelius_mode: FideliusMode = FideliusMode.ON_DEMAND
        self._fidelius_kwargs: Optional[Dict[str, Any]] = None
        self._find_fidelius_mode()

    def set_fidelius_mode(self, mode: Union[FideliusMode, str, int]):
        self._fidelius_mode = FideliusMode.from_any(mode)

    def get_fidelius_mode(self) -> FideliusMode:
        return self._fidelius_mode

    def _find_fidelius_mode(self):
        env = os.environ.get('ALVISS_FIDELIUS_MODE', FideliusMode.ON_DEMAND)
        if env == '':
            env = FideliusMode.ON_DEMAND
        self.set_fidelius_mode(env)
        if self.get_fidelius_mode() == FideliusMode.ENABLED:
            try:
                import fidelius
            except ImportError:
                log.error('ALVISS_FIDELIUS_MODE is ENABLED but fidelius is not installed')
                raise AlvissFideliusNotInstalledError('ALVISS_FIDELIUS_MODE is ENABLED but fidelius is not installed')

    @property
    def data(self) -> Dict:
        return self._data

    def load_file(self,
                  file_name: str,
                  no_resolve: bool = False,
                  no_extend: bool = False,
                  no_includes: bool = False,
                  no_env_load: bool = False,
                  no_fidelius: bool = False,
                  no_py_inject: bool = False,
                  encoding: str = 'utf-8'):
        self._skip_resolve = no_resolve
        self._skip_env_loading = no_env_load
        self._skip_includes = no_includes
        self._skip_extends = no_extend
        self._skip_fidelius = no_fidelius
        self._skip_py_inject = no_py_inject

        self._file_name = os.path.basename(file_name)
        self._file_path = os.path.dirname(os.path.abspath(file_name))
        if not os.path.exists(file_name):
            raise AlvissFileNotFoundError('File not found', file_name=file_name)

        with open(file_name, 'r', encoding=encoding) as fin:
            self.load_raw(fin.read(), no_resolve=no_resolve, no_extend=no_extend,
                          no_includes=no_includes, no_env_load=no_env_load, no_fidelius=no_fidelius)

    def _extend(self):
        if self._extends:
            for inc_file, location in self._extends:
                extended = self.__class__()

                ext_file = os.path.join(self._file_path, inc_file)
                if not os.path.exists(ext_file):
                    raise AlvissFileNotFoundError('File to extend not found', file_name=ext_file)

                extended.load_file(ext_file, no_resolve=True, no_env_load=self._skip_env_loading, no_fidelius=True)

                old_data = self._data
                old_unresolved = self._unresolved
                new_data = {}
                new_unresolved = {}
                if location:
                    iters.nested_set(new_data, location, extended.data)
                else:
                    new_data = extended.data

                for old_loc, val in extended._unresolved.items():
                    # Only if we haven't overwritten this key yet!
                    new_key = location + old_loc if location else old_loc
                    if iters.nested_get(self._data, new_key) is None:
                        new_unresolved[location + old_loc] = val

                self._data = new_data
                iters.nested_dict_update(self._data, old_data)
                self._unresolved = new_unresolved
                self._unresolved.update(old_unresolved)

    def _includes(self):
        if self._include:
            for inc_file, location in self._include:
                inc_loader = self.__class__()
                full_file = os.path.join(self._file_path, inc_file)
                if not os.path.exists(full_file):
                    raise AlvissFileNotFoundError('File to include not found', file_name=full_file)

                inc_loader.load_file(full_file, no_resolve=True, no_env_load=self._skip_env_loading, no_fidelius=True)
                new_data = {}
                new_unresolved = {}
                if location:
                    iters.nested_set(new_data, location, inc_loader.data)
                    for old_loc, val in inc_loader._unresolved.items():
                        new_unresolved[location + old_loc] = val
                else:
                    new_data = inc_loader.data
                    new_unresolved = inc_loader._unresolved
                iters.nested_dict_update(self._data, new_data)
                self._unresolved.update(new_unresolved)

    def _resolve(self):
        while self._unresolved:
            start_count = self._resolve_count

            unresolved = list(self._unresolved.items())
            for location, value in unresolved:
                res = self._check_for_var(value, location)
                # if res:  # Not sure if this will cause some unwanted side effects?
                # (e.g. overwriting something with ''?)
                if res is not None:
                    iters.nested_set(self._data, location, res)

            if start_count == self._resolve_count:
                # Loop!
                break

        # Check for required vars...
        if self._unresolved:
            required_list = []
            unresolved = list(self._unresolved.items())
            for location, value in unresolved:
                for match in list(_VAR_PATTERN.finditer(value))[::-1]:
                    key = match.group(1)
                    if key.strip().endswith('!='):
                        required_list.append((location, value))
            if required_list:
                for location, value in required_list:
                    log.error(f'Required variable config value is unresolved: {location}, {value}')
                raise AlvissSyntaxError(f'Required variable config values were unresolved: {required_list!r}')

    def _fetch_fidelius(self):
        if self._fidelius_keys:
            try:
                from fidelius.fideliusapi import FideliusFactory
                from fidelius.fideliusapi import FideliusAppProps
            except ImportError:
                if self.get_fidelius_mode() == FideliusMode.ON_DEMAND:
                    for path_tuple, value in self._fidelius_keys.items():
                        log.error(f'Fidelius tag ({path_tuple}, {value}) found but Fidelius is not installed (ALVISS_FIDELIUS_MODE=ON_DEMAND)')
                raise AlvissFideliusNotInstalledError(f'Fidelius tags found but Fidelius is not installed (ALVISS_FIDELIUS_MODE=ON_DEMAND)')

            app_var = iters.nested_get(self.data, ('app', 'slug'), iters.nested_get(self.data, ('app', 'module_name')))
            if not app_var:
                raise AlvissFideliusSyntaxError('unable to resolve fidelius keys without app.slug or app.module_name')
            group_var = iters.nested_get(self.data, ('app', 'group'))
            if not group_var:
                raise AlvissFideliusSyntaxError('unable to resolve fidelius keys without app.group')
            env_var = iters.nested_get(self.data, ('app', 'env'))
            if not env_var:
                raise AlvissFideliusSyntaxError('unable to resolve fidelius keys without app.env')

            fidcls = FideliusFactory.get_class('mock' if self.get_fidelius_mode() == FideliusMode.MOCK else 'paramstore')

            ps = fidcls(FideliusAppProps(app=app_var,
                                         group=group_var,
                                         env=env_var),
                        **self._fidelius_kwargs or {})
            done_keys = []
            for path_tuple, value in self._fidelius_keys.items():
                new_value = ps.replace(value)
                if new_value != value:
                    iters.nested_set(self._data, path_tuple, new_value)
                    done_keys.append(path_tuple)

            if done_keys:
                for k in done_keys:
                    if k in self._fidelius_keys:
                        del self._fidelius_keys[k]
                    if k in self._unresolved:
                        del self._unresolved[k]

    def _load_value(self, v: Any, path: List[str]) -> Any:
        if isinstance(v, str):
            new_v = self._check_for_var(v, path)
            if new_v is not None:
                v = new_v

        elif isinstance(v, dict):
            v = self._load_dict(v, path)

        elif isinstance(v, list):
            v = self._load_list(v, path)

        return v

    def _load_list(self, lst: List, path: List[Union[str, int]]) -> List:
        new_l = []
        for i, o in enumerate(lst):
            path.append(i)
            new_l.append(self._load_value(o, path))
            path.pop()
        return new_l

    def _load_dict(self, d: Dict, path: Optional[List[str]] = None) -> Dict:
        path = path or []
        new_d = {}
        for k, v in d.items():
            path.append(k)
            if k in self._special_key_map:
                self._special_key_map[k](v, path)

            else:
                if k.startswith('__'):
                    path.pop()
                    continue
                elif '.' in k:
                    self._chains.append((tuple(path[:-1]+k.split('.')), self._load_value(v, path)))
                else:
                    new_d[k] = self._load_value(v, path)

            path.pop()
        return new_d

    def _set_chains(self):
        for location, value in self._chains:
            if len(location) > 1:
                key = location[-1]
                location = list(location[:-1])
                value = {key: value}

            old = iters.nested_get(self._data, location) or {}
            new_value = self._load_value(value, location) or {}
            iters.nested_dict_update(old, new_value)
            iters.nested_set(self._data, location, old)

    def _check_for_var(self, value: str, path: Sequence[str]) -> Optional[str]:
        path_key = tuple(self._explode_path_strings(path))

        unresolved = False
        updated = False
        for match in list(_VAR_PATTERN.finditer(value))[::-1]:
            res = self._try_to_resolve(match, path)
            if res is not None:
                before = value
                start = value[0:match.start()]
                end = value[match.end():]
                if not start and not end:
                    value = res
                else:
                    value = value[0:match.start()]+str(res)+value[match.end():]
                if value != before:
                    updated = True
            else:
                unresolved = True

        if unresolved:
            self._unresolved[path_key] = value
        else:
            if path_key in self._unresolved:
                del self._unresolved[path_key]

        if updated:
            if isinstance(value, (str, bytes)) and _VAR_PATTERN.search(value):
                # Still more left to resolve
                self._unresolved[path_key] = value
            return value

        return None

    @staticmethod
    def _explode_path_strings(path_strings: Union[Sequence[str], str]) -> List[str]:
        new_list = []
        if not isinstance(path_strings, (tuple, list)):
            path_strings: List[str] = [path_strings]

        for path in path_strings:
            if not isinstance(path, str):
                new_list += [path]
            else:
                new_list += path.split('.')

        return new_list

    @staticmethod
    def _get_env(key: str) -> str:
        if '=' in key:
            key, default = key.split('=', 2)
            if isinstance(key, str):
                if key.endswith('!'):
                    key = key[0:-1]
            return os.environ.get(key[8:], default)
        return os.environ.get(key[8:], None)

    def _try_to_resolve(self, match: re.Match, path: Sequence[str]) -> Optional[str]:
        if not self._data or self._skip_resolve:
            return None

        key = match.group(1)

        if not self._skip_env_loading and key.startswith('__ENV__:'):
            val = self._get_env(key)
            if val is not None:
                if val == '' and key.strip().endswith('!='):
                    return None  # Still unresolved
                self._resolve_count += 1
                return val
            return match.group(0)

        if not self._skip_fidelius and key.startswith('__FID__:'):
            if self.get_fidelius_mode() == FideliusMode.DISABLED:
                return match.group(0)

            elif self.get_fidelius_mode() == FideliusMode.SUBSTITUTE_ENV:
                subst_key = f'__ENV__:{key[8:].replace(":", "__")}'
                val = self._get_env(subst_key)
                if val is not None:
                    self._resolve_count += 1
                    return val
                return match.group(0)

            self._fidelius_keys[tuple(path)] = match.group(0)

        if not self._skip_py_inject and key.startswith('__PY__:'):
            val = self._py_inject(key)
            if val is not None:
                if val == '' and key.strip().endswith('!='):
                    return None  # Still unresolved
                self._resolve_count += 1
                return val
            return match.group(0)

        val = self._get_str_key(key)
        if val is not None:
            self._resolve_count += 1
        return val

    def _py_inject(self, key: str) -> Any:
        default = None
        if '=' in key:
            key, default = key.split('=', 2)
            if isinstance(key, str):
                if key.endswith('!'):
                    key = key[0:-1]

        return strimp.get_any(key[7:], default)

    def _get_str_key(self, key: str) -> Optional[str]:
        return iters.nested_get(self._data, key.split('.'))

    def _special_key_extends(self, value: Union[str, List[str]], path: List[str]):
        if not isinstance(value, list):
            value = [value]
        self._extends.extend([(v, tuple(path[:-1])) for v in value])

    def _special_key_include(self, value: Union[str, List[str]], path: List[str]):
        if not isinstance(value, list):
            value = [value]
        self._include.extend([(v, tuple(path[:-1])) for v in value])

    def _special_key_fidelius(self, value: Dict[str, Any], path: List[str]):
        """The `__fidelius__` special key should contain a dict (map) of
        fidelius configuration values which at the moment can be:

        - `ALVISS_FIDELIUS_MODE: [ON_DEMAND|ENABLED|DISABLED|SUBSTITUTE_ENV|MOCK]` which override the environment variable if any
        - `kwargs: [dict/map]` of key/values pairs which will be given to the fidelius __init__ call and can include (for the paramstore implementation):
            - `aws_access_key_id` - overrides the `FIDELIUS_AWS_ACCESS_KEY_ID`/`AWS_ACCESS_KEY_ID` otherwise taken from environment variables
            - `aws_secret_access_key` - overrides the `FIDELIUS_AWS_SECRET_ACCESS_KEY`/`AWS_SECRET_ACCESS_KEY` otherwise taken from environment variables
            - `aws_key_arn` - overrides the `FIDELIUS_AWS_KEY_ARN` otherwise taken from environment variable
            - `aws_region_name` - overrides the `FIDELIUS_AWS_REGION_NAME`/`AWS_DEFAULT_REGION` otherwise taken from environment variable
            - `aws_endpoint_url` - overrides the `FIDELIUS_AWS_ENDPOINT_URL` otherwise taken from environment variable (if any, it's optional)
            - `flush_cache_every_time` - set to true in order to flush fidelius' cache after every call (for testing purposes)

        :param value:
        :type value:
        :param path:
        :type path:
        :return:
        :rtype:
        """
        if not isinstance(value, dict):
            log.error("The '__fidelius__' special key must be a map/dict of key/pairs")
            return

        if 'ALVISS_FIDELIUS_MODE' in value:
            self.set_fidelius_mode(value['ALVISS_FIDELIUS_MODE'])
            log.info(f'Fidelius mode loaded from `__fidelius__` special key: {self.get_fidelius_mode().name}')
            if self.get_fidelius_mode() == FideliusMode.ENABLED:
                try:
                    import fidelius
                except ImportError:
                    log.error('ALVISS_FIDELIUS_MODE is ENABLED but fidelius is not installed')
                    raise AlvissFideliusNotInstalledError('ALVISS_FIDELIUS_MODE is ENABLED but fidelius is not installed')

        if 'kwargs' in value:
            if not isinstance(value['kwargs'], dict):
                log.error("The '__fidelius__.kwargs' special key must be a map/dict of key/pairs")
                return
            self._fidelius_kwargs: Dict = value['kwargs']
            disp = self._fidelius_kwargs.copy()
            if 'aws_secret_access_key' in disp:
                disp['aws_secret_access_key'] = '********************'

            log.info(f'Fidelius kwargs loaded from `__fidelius__` special key: {disp!r}')


