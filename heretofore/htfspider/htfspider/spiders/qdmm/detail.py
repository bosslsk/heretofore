# -*- coding: utf-8 -*-
"""
create on 2018-01-24 下午6:24

author @heyao
"""

import time
import datetime

from htfspider.spiders.qidian.detail_male import QidianDetailSpider


class QdmmDetailSpider(QidianDetailSpider):
    name = 'qdmm_detail'
    redis_key = 'qdmm:detail'
    today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self):
        super(QdmmDetailSpider, self).__init__()
