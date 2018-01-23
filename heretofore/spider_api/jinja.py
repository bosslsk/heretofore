# -*- coding: utf-8 -*-
"""
create on 2018-01-23 上午9:39

author @heyao
"""

import babel


def format_datetime(value, format='%Y-%m-%d'):
    return babel.dates.format_datetime(value, format)


def seconds2hms(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return '{0:0>2}h{1:0>2}m{2:0>2}s'.format(h, m, s)
