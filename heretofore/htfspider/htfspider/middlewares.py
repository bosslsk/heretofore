# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import requests

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.downloadermiddlewares.retry import RetryMiddleware

logger = logging.getLogger(__name__)


class ErrorSaveMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    def __init__(self, settings):
        self.master_host = settings.get("MASTER_HOST")

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        # crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # crawler.signals.connect(s.process_response, signal=signals.response_received)
        crawler.signals.connect(s.process_spider_error, signal=signals.spider_error)
        return s

    # def process_response(self, response, spider):
    #     if response.status >= 400:
    #         print spider.name, response.url, response.status
    #     return response

    def process_spider_error(self, failure, response, spider):
        data = dict(error=failure.getTraceback(), url=response.url, spider=spider.name, error_type=1)
        url = 'http://{host}/api/traceback/save/{name}'.format(host=self.master_host, name=spider.name)
        data['formdata'] = response.request.body
        requests.post(url, json={'data': data})


class CustomerRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        super(CustomerRetryMiddleware, self).__init__(settings)
        if not settings.getbool('RETRY_ENABLED'):
            raise NotConfigured
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = set(int(x) for x in settings.getlist('RETRY_HTTP_CODES'))
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')
        self.master_host = settings.get("MASTER_HOST")

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            logger.debug("Retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
            retryreq = request.copy()
            retryreq.meta['retry_times'] = retries
            retryreq.dont_filter = True
            retryreq.priority = request.priority + self.priority_adjust
            return retryreq
        else:
            data = dict(
                error='TimeoutError',
                url=request.url,
                formdata=request.body,
                spider=spider.name,
                error_type=0
            )
            url = 'http://{host}/api/traceback/save/{name}'.format(host=self.master_host, name=spider.name)
            requests.post(url, json={'data': data})
            logger.debug("Gave up retrying %(request)s (failed %(retries)d times): %(reason)s",
                         {'request': request, 'retries': retries, 'reason': reason},
                         extra={'spider': spider})
