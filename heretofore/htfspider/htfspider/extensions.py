# -*- coding: utf-8 -*-
"""
create on 2018-01-16 下午2:38

author @heyao
"""

import logging

from scrapy.conf import settings
from twisted.internet import task

from scrapy.exceptions import NotConfigured
from scrapy import signals

from heretofore.utils import authorized_requests

logger = logging.getLogger(__name__)


class SpiderOnOpenClose(object):
    """Log basic scraping stats periodically"""

    def __init__(self, stats, crawler_signals, master_host, interval=60.0, total_times=5):
        self.stats = stats
        self.interval = interval
        self.master_host = master_host
        self.total_times = total_times
        self.collect_time = 0
        self.multiplier = 60.0 / self.interval
        self.task = None
        self.signals = crawler_signals

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('OOC_INTERVAL')
        total_times = crawler.settings.getfloat('OOC_TOTAL')
        master_host = crawler.settings.get('MASTER_HOST')
        if not interval or not total_times:
            raise NotConfigured
        o = cls(crawler.stats, crawler.signals, master_host, interval, total_times)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0
        self.collect_time = -1

        self.task = task.LoopingCall(self.auto_stop, spider)
        self.task.start(self.interval)
        # 发送开始消息
        authorized_requests('GET', 'http://{host}/api/ready/start/{name}'.format(host=settings.get("MASTER_HOST"), name=spider.name))
        logger.info('open spider %s' % spider.name)

    def auto_stop(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items
        if not prate and not irate:
            logger.debug('no items scraped')
            self.collect_time += 1
        else:
            self.collect_time = 0
        if self.collect_time >= self.total_times:
            logger.debug('send signal spider_closed for auto stop')
            self.signals.send_catch_log_deferred(signals.spider_closed, spider=spider, reason='auto stop')

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
        # 发送退出消息，让master发送SIGINT指令
        authorized_requests('GET', 'http://{host}/api/ready/stop/{name}'.format(host=settings.get("MASTER_HOST"), name=spider.name))
        logger.info('close spider %s, reason %s' % (spider.name, reason))
