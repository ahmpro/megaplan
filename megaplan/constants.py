# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

#: Prefix for api (first part after domain name - api version)
API_PREFIX = 'BumsCommonApiV01'

#: Digest method for request's signature
DIGEST_METHOD = 'sha1'

#: Content type should be received from api
DEFAULT_CONTENT_TYPE = 'application/json'

#: API url to get authorization data
AUTHORIZATION_URI = "/User/authorize.api"  # Only json format supported (.api extention)
