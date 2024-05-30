import unittest
import os
from alviss import quickloader
from alviss.structs.errors import *

from alviss import __version__ as expected_version

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

_HERE = os.path.dirname(__file__)


class TestPyInject(unittest.TestCase):
    def test_python_inject(self):
        config = quickloader.autoload(os.path.join(_HERE, '../res/py_inject.yaml'))
        self.assertIsInstance(config, quickloader.BaseConfig)
        self.assertEqual(expected_version, config.foo.bar.version)

    def test_python_inject_fail(self):
        config = quickloader.autoload(os.path.join(_HERE, '../res/py_inject_fail.yaml'))
        self.assertIsInstance(config, quickloader.BaseConfig)
        self.assertEqual('${__PY__:thisisnotarealmodule.__version__}', config.foo.bar.version)

    def test_python_inject_cant_fail(self):
        with self.assertRaises(AlvissSyntaxError):
            config = quickloader.autoload(os.path.join(_HERE, '../res/py_inject_cant_fail.yaml'))

    def test_python_inject_default(self):
        config = quickloader.autoload(os.path.join(_HERE, '../res/py_inject_default.yaml'))
        self.assertIsInstance(config, quickloader.BaseConfig)
        self.assertEqual('0.1.0-dev.1', config.foo.bar.version)
