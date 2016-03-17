# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals


class AuthorizationError(Exception):
    pass


class NoRequiredAttributeError(Exception):
    pass


class NoRequiredMethodError(Exception):
    pass


class DuplicatMethodNameError(Exception):
    pass


class AbstractMethodRegistrationError(Exception):
    pass


class MethodNotFoundError(Exception):
    pass


class MethodCallError(Exception):
    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def __repr__(self):
        return "<MethodCallError: {0}> {1}".format(self.status_code, self.data)

    def __str__(self):
        return self.__unicode__().decode('utf8')

    def __unicode__(self):
        return "Error code {0}: {1}".format(self.status_code, self.data)
