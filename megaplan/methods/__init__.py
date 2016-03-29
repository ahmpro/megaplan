# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import base64
import glob
import hashlib
import hmac
from email.utils import formatdate
from os.path import dirname, basename, isfile

import requests
from six import with_metaclass, b

from ..constants import DIGEST_METHOD
from ..exceptions import DuplicatMethodNameError, NoRequiredAttributeError, NoRequiredMethodError, \
    MethodNotFoundError, MethodCallError, AbstractMethodRegistrationError, BadAcceptPropertyError

modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [
    basename(f)[:-3]
    for f in modules
    if isfile(f) and not f.startswith('_') and not f.endswith('__init__.py')
    ]
__all__ += ['BaseMethod', 'methods_registry']


class BaseMethodMeta(type):
    reqired_attrs = {'_uri', '_method', }
    reqired_methods = set()

    def __new__(mcs, name, bases, namespace):
        cls = super(BaseMethodMeta, mcs).__new__(mcs, name, bases, namespace)
        if not getattr(cls, '_{}__abstract'.format(name), False) and name != 'BaseMethod':
            # Check for attributes
            reqired_attrs = mcs.reqired_attrs
            for base in bases:
                reqired_attrs.update(getattr(base, '__required_attrs', {}))
            for attr in reqired_attrs:
                if not hasattr(cls, attr) or getattr(cls, attr, None) is None:
                    raise NoRequiredAttributeError(attr, cls)

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
    __abstract = False
    _signature_cache = None
    _date_cache = None

    #: Base path part for method, e.g. User from /BumsCommonApiV01/User/authorize.api
    _parent = None

    #: Method to use for calling method
    _method = 'get'

    #: Last path part for method, e.g.  authorize from /BumsCommonApiV01/User/authorize.api
    _uri = None

    def __init__(self, host, access_id, secret_key, headers=None, accept=None):
        self._host = "{0}/".format(host.rstrip('/'))
        self._access_id = access_id
        self._secret_key = secret_key
        self._accept = accept
        self._headers_base = headers or {}
        self.input_data = None
        self._response_data = None
        self._raw_response = None

    def __call__(self, **data):
        return self.call(**data)

    def call(self, **data):
        self.input_data = data or None
        response = self._request()
        if response.status_code != 200:
            code = "HTTP {0}".format(response.status_code)
            raise MethodCallError(code, response.text)

        self._raw_response = response.text
        data = self._parse_response(response)
        self._response_data = data
        return data

    def _parse_response(self, response):
        data = None

        if self._accept == 'application/json':
            json = response.json()
            status = json.get('status')
            data = json.get('data')
            if status.get('code') != 'ok':
                raise MethodCallError(status['code'], status['message'])

        elif self._accept == 'text/xml':
            xml = response.text
            # TODO: Parse xml and format data

        else:
            raise BadAcceptPropertyError(self._accept)

        return data

    def _request(self):
        """
        Make request to the server

        :return: Response received from server
        :rtype: requests.models.Response
        """
        data = self.input_data if self._method == 'post' else None
        params = self.input_data if self._method == 'get' else None

        response = requests.request(
            method=self._method, url=self._api_url, data=data, params=params,
            headers=self._headers
        )

        return response

    @property
    def _headers(self):
        """
        Build headers for send with request

        :return: Headers
        :rtype: dict
        """
        h = self._headers_base
        h.update(
            {
                str('Accept'): str(self._accept),
                str('X-Authorization'): str("{0}:{1}".format(self._access_id, self._signature.strip())),
                str('Date'): str(self._date)
            }
        )
        return h

    @property
    def _content_type(self):
        return "application/x-www-form-urlencoded" if self._method == 'post' else ''

    @property
    def _date(self):
        """
        Calculates and cache current date

        Date must be send with headers and used in signature calculation and must be equal in both places.
        Also it must be in RFC 2822 format.

        :rtype: str
        """
        if self._date_cache is None:
            self._date_cache = formatdate(localtime=True)
        return self._date_cache

    @property
    def _signature(self):
        """
        Calculate request's signature

        :rtype: unicode
        """
        if self._signature_cache is None:
            uri = self._api_url.replace('https://', '')
            if self._method == 'get' and self.input_data:
                uri = "{0}?{1}".format(uri, "&".join(["{0}={1}".format(k, v) for k, v in self.input_data.items()]))

            s = "{method}\n\n{content_type}\n{date}\n{uri}"
            s = s.format(
                method=self._method.upper(),
                content_type=self._content_type,
                date=self._date,
                uri=uri
            )
            h = hmac.new(b(self._secret_key), b(s), getattr(hashlib, DIGEST_METHOD))
            self._signature_cache = base64.encodestring(h.hexdigest())
        return self._signature_cache

    @property
    def _api_ext(self):
        """
        Detect api url's final part based on :attr:`_accept`

        There are different api url for json and xml api requests.

        :return: API url final part (without dot)
        :rtype: unicode
        """
        if self._accept == 'application/json':
            return 'api'
        elif self._accept == 'text/xml':
            return 'xml'
        else:
            raise BadAcceptPropertyError(self._accept)

    @property
    def _api_url(self):
        """
        Build full url for the API endpoint

        :return: Full url
        :rtype: unicode
        """
        return "{0}{1}.{2}".format(self._host, self._uri.lstrip('/'), self._api_ext)


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

    @staticmethod
    def import_all():
        __import__('megaplan.methods', fromlist=["*"])


methods_registry = MethodsRegistry()
methods_registry.import_all()
