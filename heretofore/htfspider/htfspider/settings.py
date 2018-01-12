# -*- coding: utf-8 -*-

BOT_NAME = 'htfspider'

SPIDER_MODULES = ['htfspider.spiders']
NEWSPIDER_MODULE = 'htfspider.spiders'

ROBOTSTXT_OBEY = False

LOG_LEVEL = "DEBUG"

CONCURRENT_REQUESTS = 1

# COOKIES_ENABLED = False

ITEM_PIPELINES = {
    # 'htfspider.pipelines.HtfspiderPipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 300
}
REDIS_ITEMS_KEY = '%(spider)s:items'
REDIS_ITEMS_SERIALIZER = 'cPickle.dumps'

# SCRAPY_REDIS
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER_SERIALIZER = "json"
SCHEDULER_SERIALIZER = "cPickle"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
REDIS_START_URLS_AS_SET = True
REDIS_URL = 'redis://localhost:6379/0'

try:
    from _production_settings import *
except ImportError:
    pass
