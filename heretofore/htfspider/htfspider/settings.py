# -*- coding: utf-8 -*-

BOT_NAME = 'htfspider'

SPIDER_MODULES = ['htfspider.spiders']
NEWSPIDER_MODULE = 'htfspider.spiders'

ROBOTSTXT_OBEY = False

LOG_LEVEL = "DEBUG"

CONCURRENT_REQUESTS = 32

# COOKIES_ENABLED = False

ITEM_PIPELINES = {
    # 'htfspider.pipelines.HtfspiderPipeline': 300,
    'scrapy_redis.pipelines.RedisPipeline': 300
}

SPIDER_MIDDLEWARES = {
    'htfspider.middlewares.ErrorSaveMiddleware': 100
}

EXTENSIONS = {
    'scrapy.extensions.logstats.LogStats': None,
    'htfspider.extensions.SpiderOnOpenClose': 500
}

# on spider open close extension
OOC_INTERVAL = 60
OOC_TOTAL = 5

# SCRAPY_REDIS
REDIS_ITEMS_KEY = '%(spider)s:items'
REDIS_ITEMS_SERIALIZER = 'cPickle.dumps'

SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# SCHEDULER_SERIALIZER = "json"
SCHEDULER_SERIALIZER = "cPickle"
SCHEDULER_PERSIST = True
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'
REDIS_START_URLS_AS_SET = True
REDIS_URL = 'redis://localhost:6379/0'

try:
    from production_settings import *
except ImportError:
    pass
