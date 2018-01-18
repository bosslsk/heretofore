# -*- coding: utf-8 -*-
"""
create on 2017-08-28 下午5:20

author @heyao
"""

from CODES import SUCCESS


def format_dict(data, code=SUCCESS, msg='success'):
    return dict(data=data, code=code, msg=msg)
