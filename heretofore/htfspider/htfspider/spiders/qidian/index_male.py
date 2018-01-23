# -*- coding: utf-8 -*-
"""
create on 2018-01-11 下午12:23

author @heyao
"""

import re
import time
import datetime
import cPickle as pickle

import pymongo
from scrapy import Request
from scrapy.conf import settings
from scrapy_redis.spiders import RedisSpider
from htfspider.items import BookListItem


class QidianMaleIndexSpider(RedisSpider):
    name = 'qidian_index'
    redis_key = 'qidian:index'
    today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self):
        super(QidianMaleIndexSpider, self).__init__()
        mongo_uri = settings.get("MONGO_URI")
        db_name = settings.get("DB_NAME")
        auth = settings.get("AUTH")
        client = pymongo.MongoClient(mongo_uri)
        db = client[db_name]
        if auth:
            db.authenticate(**auth)
        books = set(i['book_id'] for i in db['book_index'].find({'source_id': 1}, {'book_id': 1}))
        self.books = books

    def make_request_from_data(self, data):
        data = pickle.loads(data)
        url = data.pop('data_url', None)
        if url:
            req = Request(
                url,
                meta={'data': data},
                callback=self.parse,
                dont_filter=True
            )
            return req

    def parse(self, response):
        data = response.meta['data']
        book_list = response.xpath('//ul[@class="all-img-list cf"]/li')
        for book in book_list:
            url = response.urljoin(book.xpath('./div[2]/h4/a/@href').extract()[0])
            book_id = url.split('/')[-1]
            if book_id in self.books:
                continue
            yield Request(
                url,
                meta={'data': data},
                callback=self.parse_detail,
                dont_filter=True
            )

    def parse_detail(self, response):
        sign = response.xpath('//div[@class="book-information cf"]//span[@class="blue"]/text()').extract()[1]
        if u'签约' not in sign:
            self.logger.debug('[NOT SIGN] ' + response.url)
            return
        data = response.meta['data']
        item = BookListItem()
        xpath_folder_url = '//div[@class="book-information cf"]/div[1]/a/img/@src'
        xpath_title = '//div[@class="book-information cf"]/div[2]/h1/em/text()'
        xpath_author = '//div[@class="book-information cf"]//a[@class="writer"]/text()'
        xpath_author_id = '//a[@class="writer"]/@href'
        xpath_category = '//div[@class="book-information cf"]//a[@class="red"]/text()'
        xpath_introduction = '//div[@class="book-intro"]/p/text()'
        xpath_sub_category = xpath_category
        item['url'] = response.url
        item['source_id'] = data['source_id']
        item['book_id'] = response.url.split('/')[-1]
        item['folder_url'] = response.urljoin(response.xpath(xpath_folder_url).extract()[0]).strip()
        item['title'] = response.xpath(xpath_title).extract()[0]
        item['author'] = response.xpath(xpath_author).extract()[0]
        item['author_id'] = response.xpath(xpath_author_id).extract()[0].split('=')[-1]
        item['category'] = response.xpath(xpath_category).extract()[0]
        item['sub_category'] = response.xpath(xpath_sub_category).extract()[1]
        introduction = response.xpath(xpath_introduction).extract()
        item['introduction'] = '\n'.join(p.replace(u'　', '').strip() for p in introduction)
        item['chan_id'] = re.compile(r'chanId = (\d+);').search(response.body).group()[9:-1]
        read_url = response.urljoin(response.xpath(u'//a[contains(., "免费试读")]/@href').extract()[0])
        if read_url:
            yield Request(
                read_url,
                meta={'item': item},
                callback=self.parse_published_at,
                dont_filter=True
            )
        else:
            self.logger.debug('[HAS NOT READ URL] ' + response.url)

    def parse_published_at(self, response):
        item = response.meta['item']
        published_at = response.xpath('//div[@class="info-list cf"]/ul/li[2]/em/text()').extract()[0]
        item['published_at'] = datetime.datetime.strptime(published_at, '%Y.%m.%d')
        item['status'] = 1
        item['created_at'] = self.today
        item['updated_at'] = self.today
        yield item
