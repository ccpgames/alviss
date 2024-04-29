import os
import unittest

from alviss.stubber import *
from alviss.quickloader import autoload

import logging

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

_HERE = os.path.dirname(__file__)


class TestRendering(unittest.TestCase):
    def test_class_name_maker(self):
        self.assertEqual('Foo', StubClass.field_name_to_class_name('Foo'))
        self.assertEqual('Foo', StubClass.field_name_to_class_name('foo'))
        self.assertEqual('Foo', StubClass.field_name_to_class_name('FOO'))
        self.assertEqual('FOO', StubClass.field_name_to_class_name('fOO'))

        self.assertEqual('FooBar', StubClass.field_name_to_class_name('foo_bar'))
        self.assertEqual('FooBar', StubClass.field_name_to_class_name('foo__bar'))
        self.assertEqual('FooBar', StubClass.field_name_to_class_name('fooBar'))
        self.assertEqual('FooBar', StubClass.field_name_to_class_name('FooBar'))
        self.assertEqual('FooBar', StubClass.field_name_to_class_name('Foo_Bar'))
        self.assertEqual('FooBAR', StubClass.field_name_to_class_name('FooBAR'))
        self.assertEqual('FooBAR', StubClass.field_name_to_class_name('foo_B_A_R'))

        self.assertEqual('PaulWantsSomePizza', StubClass.field_name_to_class_name('PaulWantsSomePizza'))
        self.assertEqual('PaulWantsSomePizza', StubClass.field_name_to_class_name('paul_wants_some_pizza'))
        self.assertEqual('PaulWantsSomePizza', StubClass.field_name_to_class_name('Paul_Wants_Some_Pizza'))
        self.assertEqual('PaulWantsSomePizza', StubClass.field_name_to_class_name('PaulWants_some_pizza'))
        self.assertEqual('PaulWantsSomePizza', StubClass.field_name_to_class_name('PaulWants_some____pizza'))
        self.assertEqual('PaulWantsSomePIZZA', StubClass.field_name_to_class_name('PaulWants_some____PIZZA'))
        self.assertEqual('PaulWantsSomePizza', StubClass.field_name_to_class_name('PAUL_WANTS_SOME_PIZZA'))

    def test_simple(self):
        file = os.path.join(_HERE, '../res/stubber/simple.yaml')
        expected_file = os.path.join(_HERE, '../res/stubber/expected/simple.py')
        stubs = SimpleStubMaker().render_stub_classes_from_descriptor_file(file, is_private=True)

        stub_lines = [line.rstrip() for line in stubs.split('\n')]
        with open(expected_file, 'r') as fin:
            expected_lines = [line.rstrip() for line in fin]

        self.assertEqual(len(expected_lines), len(stub_lines))

        for i in range(len(expected_lines)):
            self.assertEqual(expected_lines[i], stub_lines[i], f'Mismatch in line {i + 1}')

        from tests.res.stubber.expected.simple import AlvissConfigStub
        cfg: AlvissConfigStub = autoload(os.path.join(_HERE, '../res/stubber/simple_data.yaml'))  # noqa
        self.assertEqual(42, cfg.collapsed.group.in_.one.string)
        self.assertEqual(42, cfg.collapsed.group['in']['one']['string'])

    def test_required_children(self):
        file = os.path.join(_HERE, '../res/stubber/required_by_child.yaml')
        expected_file = os.path.join(_HERE, '../res/stubber/expected/required_by_child.py')
        stubs = SimpleStubMaker().render_stub_classes_from_descriptor_file(file, is_private=False)

        stub_lines = [line.rstrip() for line in stubs.split('\n')]
        with open(expected_file, 'r') as fin:
            expected_lines = [line.rstrip() for line in fin.readlines()]

        self.assertEqual(len(expected_lines), len(stub_lines))

        for i in range(len(expected_lines)):
            self.assertEqual(expected_lines[i], stub_lines[i], f'Mismatch in line {i+1}')

    def test_with_complex_lists(self):
        file = os.path.join(_HERE, '../res/stubber/with_complex_lists.yaml')
        expected_file = os.path.join(_HERE, '../res/stubber/expected/with_complex_lists.py')
        stubs = SimpleStubMaker().render_stub_classes_from_descriptor_file(file, class_name='', is_private=False)

        stub_lines = [line.rstrip() for line in stubs.split('\n')]
        with open(expected_file, 'r') as fin:
            expected_lines = [line.rstrip() for line in fin.readlines()]

        with self.subTest(exp_len=len(expected_lines), stb_len=len(stub_lines)):
            self.assertEqual(len(expected_lines), len(stub_lines))

        for i in range(len(expected_lines)):
            with self.subTest(exp=expected_lines[i], stb=stub_lines[i], i=i):
                self.assertEqual(expected_lines[i], stub_lines[i], f'Mismatch in line {i + 1}')

        self.assertEqual(expected_lines, stub_lines)

    def test_with_lists_of_dicts(self):
        file = os.path.join(_HERE, '../res/stubber/with_lists_of_dicts.yaml')
        expected_file = os.path.join(_HERE, '../res/stubber/expected/with_lists_of_dicts.py')
        stubs = SimpleStubMaker().render_stub_classes_from_descriptor_file(file, class_name='', is_private=True)

        stub_lines = [line.rstrip() for line in stubs.split('\n')]
        with open(expected_file, 'r') as fin:
            expected_lines = [line.rstrip() for line in fin.readlines()]

        with self.subTest(exp_len=len(expected_lines), stb_len=len(stub_lines)):
            self.assertEqual(len(expected_lines), len(stub_lines))

        for i in range(len(expected_lines)):
            with self.subTest(exp=expected_lines[i], stb=stub_lines[i], i=i):
                self.assertEqual(expected_lines[i], stub_lines[i], f'Mismatch in line {i + 1}')

        self.assertEqual(expected_lines, stub_lines)

    def test_with_complex_maps_and_lists(self):
        file = os.path.join(_HERE, '../res/stubber/with_complex_maps_and_lists.yaml')
        expected_file = os.path.join(_HERE, '../res/stubber/expected/with_complex_maps_and_lists.py')
        stubs = SimpleStubMaker().render_stub_classes_from_descriptor_file(file, class_name='ComplexConfig', is_private=False)

        stub_lines = [line.rstrip() for line in stubs.split('\n')]
        with open(expected_file, 'r') as fin:
            expected_lines = [line.rstrip() for line in fin.readlines()]

        with self.subTest(exp_len=len(expected_lines), stb_len=len(stub_lines)):
            self.assertEqual(len(expected_lines), len(stub_lines))

        for i in range(len(expected_lines)):
            with self.subTest(exp=expected_lines[i], stb=stub_lines[i], i=i):
                self.assertEqual(expected_lines[i], stub_lines[i], f'Mismatch in line {i + 1}')

        self.assertEqual(expected_lines, stub_lines)