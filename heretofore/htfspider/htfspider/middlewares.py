# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals


class ErrorSaveMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        # crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        # crawler.signals.connect(s.process_response, signal=signals.response_received)
        crawler.signals.connect(s.process_spider_error, signal=signals.spider_error)
        return s

    # def process_response(self, response, spider):
    #     if response.status >= 400:
    #         print spider.name, response.url, response.status
    #     return response

    def process_spider_error(self, failure, response, spider):
        error = [{'func': e[0], 'file': '/'.join(e[1].rsplit('/', 4)[-4:]), 'error_no': e[2]} for e in failure.frames if
                 'htfspider' in e[1]]
        print dict(error=error, url=response.url, spider=spider.name)
