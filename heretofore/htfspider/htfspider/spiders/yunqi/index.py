# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/21 19:31
    @subject: 云起小说网 http://yunqi.qq.com
"""
import time
import json
import cPickle as pickle
from datetime import datetime

import pymongo
from scrapy import Request
from scrapy.conf import settings
from scrapy_redis.spiders import RedisSpider

from htfspider.items import BookListItem


class YunqiIndexSpider(RedisSpider):
    name = 'yunqi_index'
    redis_key = 'yunqi:index'
    today = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def __init__(self):
        super(YunqiIndexSpider, self).__init__()
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
        elements = response.xpath('//div[@class="book"]')
        for element in elements:
            url = response.urljoin(element.xpath('./a/@href').extract()[0])
            yield Request(
                url,
                callback=self.parse_detail,
                dont_filter=True
            )

    def parse_detail(self, response):
        if '小说不存在' in response.body:
            self.logger.debug('[NO THIS BOOK]' + response.url)
            return
        sign = response.xpath('//div[@class="y"]/a/text()').extract()[0]
        if '签约' not in sign:
            self.logger.debug('[NO SIGN]' + response.url)
            return
        item = BookListItem()
        item['source_id'] = 11
        item['status'] = 1
        item['url'] = response.url
        item['book_id'] = item['url'].split('/')[-1].split('.')[0]
        item['title'] = response.xpath('//div[@class="title"]/strong/a/text()').extract()[0]
        try:
            item['author'] = response.xpath('//div[@class="au_name"]/p[2]/a/text()').extract()[0]
        except IndexError:
            item['author'] = response.xpath('//div[@id="authorWeixinContent"]/text()').extract()[0].split('：')[0][:-1]
        item['category'] = response.xpath('//div[@class="title"]/a/text()').extract()[1]
        item['sub_category'] = response.xpath('//div[@class="title"]/a/text()').extract()[2]
        item['introduction'] = '\n'.join(response.xpath('//div[@class="info"]/p/text()').extract())
        item['created_at'] = self.today
        item['updated_at'] = self.today
        published_url = 'http://android.reader.qq.com/v6_3_5/nativepage/book/detail?bid={}'.format(item['book_id'])
        yield Request(
            url=published_url,
            meta={'item': item},
            callback=self.parse_published_at,
            dont_filter=True
        )

    def parse_published_at(self, response):
        item = response.meta['item']
        published_json = json.loads(response.body)
        if published_json['code']:
            return
        published_at = published_json['introinfo']['book']['publishtime'].split(' ')[0]
        item['published_at'] = datetime.strptime(published_at, '%Y-%m-%d')
        yield item
