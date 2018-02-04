# -*- coding: utf-8 -*-
"""
create on 2018-01-24 下午6:24

author @heyao
"""

import time
import datetime

from htfspider.spiders.qidian.index_male import QidianMaleIndexSpider


class QdmmIndexSpider(QidianMaleIndexSpider):
    name = 'qdmm_index'
    redis_key = 'qdmm:index'
    today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self, **kwargs):
        super(QdmmIndexSpider, self).__init__(**kwargs)
