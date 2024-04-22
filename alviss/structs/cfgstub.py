__all__ = [
    '_BaseCfgStub',
]
from ._base import *


class _BaseCfgStub(Protocol):
    """This is the base Protocol for all generated Stubs

    """
    def __getattr__(self, item) -> Union[Any, Empty]:
        ...
