# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

from . import BaseMethod, methods_registry


class BaseEmployee(BaseMethod):
    __abstract = True
    _parent = 'Employee'


@methods_registry('Card')
class Card(BaseEmployee):
    _uri = 'BumsStaffApiV01/Employee/card'
