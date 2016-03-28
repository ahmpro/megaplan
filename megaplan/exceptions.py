# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals


class AuthorizationError(Exception):
    """Authorization failed"""
    pass


class NoRequiredAttributeError(Exception):
    """API method miss some of required attributes"""
    pass


class NoRequiredMethodError(Exception):
    """API method miss some of required methods"""
    pass


class DuplicatMethodNameError(Exception):
    """API method with this name already registred"""
    pass


class AbstractMethodRegistrationError(Exception):
    """Trying to register API method's class marked as abstract"""
    pass


class MethodNotFoundError(Exception):
    """Required API method have no registred class"""
    pass


class BadAcceptPropertyError(Exception):
    """Invalid string specified for `accept` parametr"""
    pass


class MethodCallError(Exception):
    """
    There is an error while calling API method

    API server returns some error in response
    """

    def __init__(self, status_code, data):
        self.status_code = status_code
        self.data = data

    def __repr__(self):
        return "<MethodCallError: {0}> {1}".format(self.status_code, self.data)

    def __str__(self):
        return self.__unicode__().decode('utf8')

    def __unicode__(self):
        return "Error code {0}: {1}".format(self.status_code, self.data)
