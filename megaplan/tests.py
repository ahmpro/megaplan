# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import unittest

from megaplan.api import API
from megaplan.exceptions import MethodNotFoundError
from megaplan.methods import BaseMethod
from megaplan.methods import methods_registry


class TestApi(unittest.TestCase):
    def setUp(self):
        methods_registry.clean()

    def test_method_resolve_success(self):
        @methods_registry('test')
        class TestMethod(BaseMethod):
            uri = ''

        api = API()
        api.account = 'testacc'
        self.assertTrue(api.test)
        self.assertEqual(api.test.host, 'https://testacc.megaplan.ru')

    def test_method_resolve_error(self):
        api = API()
        self.assertRaises(AttributeError, lambda: api.notfoud)
        self.assertRaises(MethodNotFoundError, lambda: api.call('notfound'))


if __name__ == '__main__':
    unittest.main()
