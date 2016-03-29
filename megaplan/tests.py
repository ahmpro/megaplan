# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import os
import unittest

from megaplan.api import API
from megaplan.exceptions import MethodNotFoundError, AuthorizationError
from megaplan.methods import BaseMethod
from megaplan.methods import methods_registry

test_account = os.environ.get('TEST_ACCOUNT')
test_login = os.environ.get('TEST_LOGIN')
test_pasword = os.environ.get('TEST_PASSWORD')


@methods_registry('test')
class TestMethod(BaseMethod):
    _uri = 'testmethod'


class TestApi(unittest.TestCase):
    def test_method_resolve_success(self):
        api = API('test')
        self.assertTrue(api.test)
        print(methods_registry.items())
        self.assertEqual(len(methods_registry._registry), 2)

    def test_urls(self):
        api = API('testacc')
        self.assertEqual(api.test._host, 'https://testacc.megaplan.ru/')
        self.assertEqual(api.test._api_url, 'https://testacc.megaplan.ru/testmethod.api')
        api.accept = 'text/xml'
        self.assertEqual(api.test._api_url, 'https://testacc.megaplan.ru/testmethod.xml')

    def test_method_resolve_error(self):
        api = API('test')
        self.assertRaises(AttributeError, lambda: api.notfoud)
        self.assertRaises(MethodNotFoundError, lambda: api.call('notfound'))

    @unittest.skipIf(
        not all([test_account, test_login, test_pasword]),
        'authentication test skipped - no authentication test data'
    )
    def test_authentication(self):
        try:
            api = API.configure(test_account, test_login, test_pasword)
        except AuthorizationError:
            self.fail('Authorization failed')

        self.assertTrue(api.secret_key)
        self.assertTrue(api.access_id)

    @unittest.skipIf(
        not all([test_account, test_login, test_pasword]),
        'authentication test skipped - no authentication test data'
    )
    def test_methods_works(self):
        api = API.configure(test_account, test_login, test_pasword)
        self.assertTrue('employee' in api.call('Employee_Card', Id=api.employee_id))
