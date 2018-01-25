# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/24 10:55
    @subject: 潇湘书院 http://www.xxsy.net/
"""
import re
import time
from datetime import datetime
import cPickle as pickle

import pymongo
from scrapy.conf import settings
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from htfspider.items import BookListItem


class XxsyIndexSpider(RedisSpider):
    name = 'xxsy_index'
    redis_key = 'xxsy:index'
    today = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self):
        super(XxsyIndexSpider, self).__init__()
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
                callback=self.parse,
                dont_filter=True
            )
            return req

    def parse(self, response):
        elements = response.xpath('//div[@class="result-list"]/ul/li')
        for element in elements:
            url = response.urljoin(element.xpath('./a/@href').extract()[0])
            yield Request(
                url,
                callback=self.parse_detail,
                dont_filter=True
            )

    def parse_detail(self, response):
        sign = response.xpath('//p[@class="sub-cols"]/span/text()').extract()[0]
        if u'公众' in sign:
            self.logger.debug('[NOT SIGN]' + response.url)
            return
        item = BookListItem()
        item['url'] = response.url
        item['book_id'] = response.url.split('/')[-1].split('.')[0]
        item['source_id'] = 6
        item['folder_url'] = response.xpath('//dl[@class="bookprofile"]/dt/img/@src').extract()[0]
        item['title'] = response.xpath('//div[@class="title"]/h1/text()').extract()[0]
        item['author'] = response.xpath('//div[@class="title"]/span/a/text()').extract()[0]
        item['category'] = response.xpath('//p[@class="sub-cols"]/span/text()').extract()[2].strip().split(u'：')[-1]
        item['sub_category'] = ''
        item['introduction'] = '\n'.join(response.xpath('//dl[@class="introcontent"]/dd/p/text()').extract())
        item['status'] = 1
        item['created_at'] = self.today
        item['updated_at'] = self.today
        read_url = response.urljoin(response.xpath('//a[@class="btn_read"]/@href').extract()[0])
        yield Request(
            url=read_url,
            meta={'item': item},
            callback=self.parse_published_at,
            dont_filter=True
        )

    def parse_published_at(self, response):
        item = response.meta['item']
        published_at = response.xpath('//p[@class="chapter-subtitle"]/text()').extract()[3]
        item['published_at'] = datetime.strptime(re.findall(r'(\d{4}-\d+-\d+)', published_at)[0], '%Y-%m-%d')
        yield item
