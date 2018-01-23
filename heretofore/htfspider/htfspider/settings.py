# -*- coding: utf-8 -*-

BOT_NAME = 'htfspider'

SPIDER_MODULES = ['htfspider.spiders']
NEWSPIDER_MODULE = 'htfspider.spiders'

# ROBOTSTXT_OBEY = False

LOG_LEVEL = "DEBUG"
LOG_FILE = '/Users/heyao/Desktop/htf_spider.log'

CONCURRENT_REQUESTS = 64

DOWNLOAD_TIMEOUT = 5
RETRY_TIMES = 5

COOKIES_ENABLED = False

ITEM_PIPELINES = {
    'htfspider.pipelines.HtfspiderPipeline': 310,
    # 'scrapy_redis.pipelines.RedisPipeline': 300
}

SPIDER_MIDDLEWARES = {
    'htfspider.middlewares.ErrorSaveMiddleware': 300,
}

DOWNLOADER_MIDDLEWARES = {
    'htfspider.middlewares.CustomerRetryMiddleware': 200,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

EXTENSIONS = {
    'scrapy.extensions.logstats.LogStats': None,
    'htfspider.extensions.SpiderOnOpenClose': 500
}

# on spider open close extension
OOC_INTERVAL = 30  # seconds
OOC_TOTAL = 2  # times

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

# mongodb
MONGO_URI = 'mongodb://localhost:27017'
DB_NAME = 'htf_spider'
AUTH = {}

# master settings
MASTER_HOST = 'localhost'
MASTER_PORT = '8001'

try:
    from production_settings import *
except ImportError:
    pass
