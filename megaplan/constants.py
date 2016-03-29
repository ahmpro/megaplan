# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, unicode_literals

#: Digest method for request's signature
DIGEST_METHOD = 'sha1'

#: Content type should be received from api
DEFAULT_CONTENT_TYPE = 'application/json'

#: API url to get authorization data
AUTHORIZATION_URI = "BumsCommonApiV01/User/authorize.api"  # Only json format supported (.api extention)
