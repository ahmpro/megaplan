# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

import base64
import hmac
from email.utils import formatdate

import requests
from six import with_metaclass

from ..constants import DIGEST_METHOD, API_PREFIX
from ..exceptions import DuplicatMethodNameError, NoRequiredAttributeError, NoRequiredMethodError, \
    MethodNotFoundError, MethodCallError, AbstractMethodRegistrationError, BadAcceptPropertyError

__all__ = ['BaseMethod', 'methods_registry']


class BaseMethodMeta(type):
    reqired_attrs = {'_uri', '_method', }
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


class BaseMethod(with_metaclass(BaseMethodMeta)):
    """Base class for methods"""
    __metaclass__ = BaseMethodMeta
    _abstract = False
    _signature_cache = None
    _date_cache = None
    _response_data = None

    #: Base path part for method, e.g. User from /BumsCommonApiV01/User/authorize.api
    _parent = None

    #: Method to use for calling method
    _method = 'post'

    #: Last path part for method, e.g.  authorize from /BumsCommonApiV01/User/authorize.api
    _uri = None

    def __init__(self, host, access_id, secret_key, headers=None, accept=None):
        self._host = "{0}/".format(host.rstrip('/'))
        self._access_id = access_id
        self._secret_key = secret_key
        self._accept = accept
        self._headers_base = headers or {}
        self.input_data = None

    def __call__(self, **data):
        return self.call(**data)

    def call(self, **data):
        self.input_data = data or None
        response = self._request()
        if response.status_code != 200:
            raise MethodCallError(response.status_code, response.text)

        if self._accept == 'application/json':
            json = response.json()
            status = json['status']
            data = json['data']
            if status['code'] == 'error':
                raise MethodCallError(status['code'], status['message'])
        elif self._accept == 'text/xml':
            xml = response.text
            # TODO: Parse xml and format data

        self._response_data = data
        return data

    def _request(self):
        data = self.input_data if self._method == 'post' else None
        params = self.input_data if self._method == 'get' else None
        response = requests.request(
            method=self._method, url=self._url, data=data, params=params,
            headers=self._headers
        )

        return response

    @property
    def _headers(self):
        h = self._headers_base
        h.update(
            {
                str('Accept'): str(self._accept),
                str('X-Authorization'): str("{0}:{1}".format(self._access_id, self._signature)),
                str('Date'): str(self._date)
            }
        )
        return h

    @property
    def _content_type(self):
        return "application/x-www-form-urlencoded" if self._method == 'post' else ''

    @property
    def _date(self):
        if self._date_cache is None:
            self._date_cache = formatdate(localtime=True)
        return self._date_cache

    @property
    def _signature(self):
        if self._signature_cache is None:
            s = "{method}\n\n{content_type}\n{date}\n{host}\n{uri}"
            s = s.format(
                method=self._method,
                content_type=self._content_type,
                date=self._date,
                host=self._host,
                uri=self._uri
            )
            h = hmac.new(self._secret_key, s, DIGEST_METHOD)
            self._signature_cache = base64.encodestring(h.hexdigest())
        return self._signature_cache

    @property
    def _ext(self):
        if self._accept == 'application/json':
            return 'api'
        elif self._accept == 'text/xml':
            return 'xml'
        else:
            raise BadAcceptPropertyError(self._accept)

    @property
    def _url(self):
        return "{0}{1}/{2}.{3}".format(self._host, API_PREFIX, self._uri.lstrip('/'), self._ext)


class MethodsRegistry(object):
    """Registry of all methods"""
    __slots__ = ('_registry',)

    def __init__(self):
        self._registry = {}

    def __call__(self, name=None):
        """
        Registry decorator

        :param unicode name: name of registred method (by default - class's name)
        """
        def f(cls):
            n = name or cls.__name__
            self.register(n, cls)
            return cls
        return f

    def register(self, name, cls):
        """
        Register method's class with specified name

        :param unicode name: Method's name
        :param BaseMethod cls: Method's class
        """

        if '_' not in name:
            parent = cls._parent
            if parent:
                name = "{0}_{1}".format(parent, name)

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

    def clean(self):
        self._registry = {}


methods_registry = MethodsRegistry()
