# -*- coding: utf-8 -*-
"""
create on 2017-09-06 下午3:43

author @heyao
"""

from CODES import *


class ApiExceptions(Exception):
    error_code = PAGE_NOT_FOUND

    def __init__(self, code=None, payload=None, msg='not found'):
        super(ApiExceptions, self).__init__(self)
        if code is not None:
            self.code = code
        self.payload = payload
        self.msg = msg

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['code'] = self.code
        rv['msg'] = self.msg
        rv['data'] = None
        return rv


class BadRequest(ApiExceptions):
    def __init__(self, code=BAD_REQUEST, payload=None, msg='Bad Request'):
        super(BadRequest, self).__init__(code, payload, msg)


class ComingSoon(ApiExceptions):
    def __init__(self, code=SUCCESS, payload=None, msg='coming soon'):
        super(ComingSoon, self).__init__(code, payload, msg)
