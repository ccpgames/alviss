__all__ = [
    'IStubMaker',
]
from alviss.structs import *


class IStubMaker(abc.ABC):
    @abc.abstractmethod
    def render_stub_classes_from_descriptor_file(self, file) -> str:
        pass
