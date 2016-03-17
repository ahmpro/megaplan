# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import unittest

from megaplan.methods import BaseMethod, methods_registry, NoRequiredAttributeError


class TestMethods(unittest.TestCase):
    def test_registry(self):
        @methods_registry('test')
        class TestMethod(BaseMethod):
            uri = ''

        self.assertTrue('test' in methods_registry)

        @methods_registry()
        class NoName(BaseMethod):
            uri = ''

        self.assertTrue(issubclass(methods_registry.get('NoName'), BaseMethod))
        self.assertTrue('NoName' in methods_registry)
        self.assertEqual(len(methods_registry), 2)

    def test_methods_creation(self):
        self.assertRaises(NoRequiredAttributeError, self._create_bad_method, )

    def _create_bad_method(self):
        class NoName(BaseMethod):
            pass
