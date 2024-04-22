__all__ = [
    'IStaticRenderer',
]
import abc


class IStaticRenderer(abc.ABC):
    @abc.abstractmethod
    def render_static_config_from_file(self, file: str) -> str:
        """Renders a single static configuration file from an Alviss formatted
        file, including all included and/or extended files and resolving all
        expressions, variables and internal references and such.
        """
        pass

    @abc.abstractmethod
    def render_static_config_to_file(self, input_file: str, output_file: str, overwrite_existing: bool = False):
        """Writer the results of the `render_static_config_from_file` call to
        the given output file.
        """
        pass
