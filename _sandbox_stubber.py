from alviss import quickloader
from alviss.stubber.stubmaker._simple import SimpleStubMaker
from alviss.stubber.stubmaker._structs import StubClass
from alviss.stubber.stubmaker._structs import StubField

import os
import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

_HERE = os.path.dirname(__file__)

_FILE = os.path.join(_HERE, 'tests/res/stubber/with_lists_of_dicts.yaml')


if __name__ == '__main__':
    stubs = SimpleStubMaker().render_stub_classes_from_descriptor_file(_FILE)
    with open('_tmp_list_of_dicts.txt', 'w') as fout:
        fout.write(stubs)
