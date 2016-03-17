# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import base64
import hmac
from email.utils import formatdate

import requests

from ..constants import DEFAULT_CONTENT_TYPE, DIGEST_METHOD
from ..exceptions import DuplicatMethodNameError, NoRequiredAttributeError, NoRequiredMethodError, \
    MethodNotFoundError, MethodCallError, AbstractMethodRegistrationError

__all__ = ['BaseMethod', 'methods_registry']


class BaseMethodMeta(type):
    reqired_attrs = {'uri'}
    reqired_methods = set()

    def __new__(mcs, name, bases, namespace):
        cls = super(BaseMethodMeta, mcs).__new__(mcs, name, bases, namespace)
        if not getattr(cls, '_abstract', False) and name != 'BaseMethod':
            # Check for attributes
            reqired_attrs = mcs.reqired_attrs
            for base in bases:
                reqired_attrs.update(getattr(base, '__required_attrs', {}))
            for attr in reqired_attrs:
                if not hasattr(cls, attr) or getattr(cls, attr, None) is None:
                    raise NoRequiredAttributeError(attr)

            # Check for methods
            reqired_methods = mcs.reqired_methods
            for base in bases:
                reqired_methods.update(getattr(base, '__required_methods', {}))
            for meth in reqired_methods:
                if not hasattr(cls, meth) or not callable(getattr(cls, meth)):
                    raise NoRequiredMethodError(meth)
        return cls


class BaseMethod(object):
    """Base class for methods"""
    __metaclass__ = BaseMethodMeta
    _abstract = False
    _signature = None
    _date = None

    method = 'post'
    uri = None

    def __init__(self, host, access_id, secret_key, headers=None, accept=DEFAULT_CONTENT_TYPE):
        self.host = host.rstrip('/')
        self.access_id = access_id
        self.secret_key = secret_key
        self.accept = accept
        self._headers = headers or {}
        self.data = None

    def __call__(self, **data):
        return self.call(**data)

    def call(self, **data):
        self.data = data or None
        response = self._request()
        if response.status_code != 200:
            raise MethodCallError(response.status_code, response.text)

        json = response.json()
        status = json['status']
        data = json['data']
        if status['code'] == 'error':
            raise MethodCallError(status['code'], status['message'])

        return data

    def _request(self):
        data = self.data if self.method == 'post' else None
        params = self.data if self.method == 'get' else None
        response = requests.request(
            method=self.method, url=self.url, data=data, params=params,
            headers=self.headers
        )

        return response

    @property
    def headers(self):
        h = self._headers
        h.update(
            {
                str('Accept'): str(self.accept),
                str('X-Authorization'): str("{0}:{1}".format(self.access_id, self.signature)),
                str('Date'): str(self.date)
            }
        )
        return h

    @property
    def content_type(self):
        return "application/x-www-form-urlencoded" if self.method == 'post' else ''

    @property
    def date(self):
        if self._date is None:
            self._date = formatdate(localtime=True)
        return self._date

    @property
    def signature(self):
        if self._signature is None:
            s = "{method}\n\n{content_type}\n{date}\n{host}\n{uri}"
            s = s.format(
                method=self.method,
                content_type=self.content_type,
                date=self.date,
                host=self.host,
                uri=self.uri
            )
            h = hmac.new(self.secret_key, s, DIGEST_METHOD)
            self._signature = base64.encodestring(h.hexdigest())
        return self._signature

    @property
    def url(self):
        return "{0}/{1}".format(self.host, self.uri.lstrip('/'))


class MethodsRegistry(object):
    """Registry of all methods"""
    __slots__ = ('_registry',)
    _registry = {}

    def __call__(self, name=None):
        """
        Registry decorator

        :param unicode name: name of registred method (by default - class's name)
        """
        def f(cls):
            self.register(name or cls.__name__, cls)
            return cls
        return f

    def register(self, name, cls):
        """
        Register method's class with specified name

        :param unicode name: Method's name
        :param BaseMethod cls: Method's class
        """
        if name in self._registry:
            raise DuplicatMethodNameError(name)

        if getattr(cls, "_abstract", False):
            raise AbstractMethodRegistrationError(cls)

        self._registry[name] = cls

    def get(self, name):
        """
        Get method's class by name

        :param unicode name: Method's name
        :return: Method's class
        :rtype: BaseMethod
        """
        meth = self._registry.get(name)
        if not meth:
            raise MethodNotFoundError(name)
        return meth

    def values(self):
        """
        List of all method's classes

        :return: List of classes
        :rtype: list[BaseMethod]
        """
        return self._registry.values()

    def items(self):
        """
        List of tuples (name, class)

        :return: List of tuples
        :rtype: list[unicode,BaseMethod]
        """
        return self._registry.items()

    def __contains__(self, item):
        return item in self._registry

    def __len__(self):
        return len(self._registry)

    def __iter__(self):
        return iter(self._registry)


methods_registry = MethodsRegistry()
