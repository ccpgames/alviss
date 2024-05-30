__all__ = [
    'IAlvissLoader',
    'FideliusMode',
]

from alviss.structs import *


class FideliusMode(EnumEx):
    """Setting the environment variable ALVISS_FIDELIUS_MODE to any of these
    strings will override the default Fidelius functionality.

    E.g. this will just disable Fidelius:
    ```bash
    export ALVISS_FIDELIUS_MODE=DISABLED
    ```
    """
    ON_DEMAND = 0  # Load and use Fidelius if __FID__ tags are encountered (default)
    ENABLED = 1  # Load Fidelius on startup
    DISABLED = 2  # Fidelius is disabled and __FID__ tags are ignored
    SUBSTITUTE_ENV = 3  # Fidelius is disabled and __FID__ are substituted by __ENV__ (e.g. for testing or dev)
    MOCK = 4  # Fidelius is enabled but the Mock instance will be used (for testing and/or dev)


class IAlvissLoader(abc.ABC):
    @abc.abstractmethod
    def set_fidelius_mode(self, mode: Union[FideliusMode, str, int]):
        """Manually sets the operational mode of Fidelius. Otherwise it's
        determined by the `ALVISS_FIDELIUS_MODE` environment variable.
        """
        pass

    @abc.abstractmethod
    def get_fidelius_mode(self) -> FideliusMode:
        """Returns the current operational mode of Fidelius.
        """
        pass

    @abc.abstractmethod
    def load_file(self,
                  file_name: str,
                  no_resolve: bool = False,
                  no_extend: bool = False,
                  no_includes: bool = False,
                  no_env_load: bool = False,
                  no_fidelius: bool = False,
                  no_py_inject: bool = False,
                  encoding: str = 'utf-8'):
        """Loads a config file.

        :param file_name: The file to load.
        :param no_resolve: Skips resolving any special tags
        :param no_extend:
        :param no_includes:
        :param no_env_load:
        :param no_fidelius:
        :param no_py_inject:
        :param encoding:
        """
        pass

    # @abc.abstractmethod
    # def load_url(self, url: str):
    #     pass

    @abc.abstractmethod
    def load_raw(self, raw_data: str, no_resolve: bool = False,
                 no_extend: bool = False, no_includes: bool = False, no_env_load: bool = False,
                 no_fidelius: bool = False, no_py_inject: bool = False):
        """Loads configuration data directly from a string.

        The `load_file` method basically just reads a file and passes its
        content to this method in most cases."""
        pass

    @property
    @abc.abstractmethod
    def data(self) -> Dict:
        """A python dict with the raw configuration values loaded and parsed
        """
        pass

    @property
    @abc.abstractmethod
    def rendered(self) -> str:
        """A string of the configuration values loaded and parser in the same
        format as the initial input format
        """
        pass
