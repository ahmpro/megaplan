# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import hashlib

import requests

from .constants import AUTHORIZATION_URI, DEFAULT_CONTENT_TYPE
from .exceptions import AuthorizationError
from .methods import methods_registry


class API(object):
    account = None

    access_id = None
    secret_key = None
    user_id = None
    employee_id = None
    methods = methods_registry

    _host = "https://{account}.megaplan.ru/"
    accept = DEFAULT_CONTENT_TYPE

    @classmethod
    def configure(cls, account, login, password):
        cls.account = account
        api = cls()
        api._authorize(login=login, password=password)

        return api

    @property
    def host(self):
        return self._host.format(account=self.account)

    def _authorize(self, login, password):
        params = {'Login': login, 'Password': hashlib.md5(password).hexdigest()}
        response = requests.get("{0}{1}".format(self.host, AUTHORIZATION_URI), params=params)
        if response.status_code == 200:
            json = response.json()
            status = json['status']
            if status['code'] == 'ok':
                data = json['data']
                self.access_id = data.get('AccessId')
                self.secret_key = data.get('SecretKey')
                self.user_id = data.get('UserId')
                self.employee_id = data.get('EmployeeId')
                if not self.access_id or not self.secret_key:
                    raise AuthorizationError(
                        "access_id: {0}, secret_key: {1}".format(self.access_id, self.secret_key)
                    )
            else:
                raise AuthorizationError(
                    "Error code: {0}, message: {1}".format(status['code'], status['message'])
                )
        else:
            raise AuthorizationError("Http code: {0}".format(response.status_code))

    def __getattr__(self, item):
        if item in self.methods:
            return self.methods.get(item)(self.host, self.access_id, self.secret_key, self.accept)
        return super(API, self).__getattribute__(item)

    def call(self, method, **kwargs):
        m = self.methods.get(method)(self.host, self.access_id, self.secret_key, self.accept)
        return m(**kwargs)

    def __call__(self, method, **kwargs):
        return self.call(method, **kwargs)
