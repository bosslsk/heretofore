# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/21 19:31
    @subject: 创世中文网 http://chuangshi.qq.com
"""
import time
import json
from datetime import datetime
import cPickle as pickle

from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from htfspider.items import BookListItem


class ChuangshiIndexSpider(RedisSpider):
    name = 'chuangshi_index'
    redis_key = 'chuangshi:index'
    today = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def make_requests_from_url(self, data):
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
        elements = response.xpath('//div[@class="leftlist"]/table/tr')[1:]
        for element in elements:
            url = response.urljoin(element.xpath('./td/a/@href').extract()[1])
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
        item['url'] = response.url
        item['book_id'] = item['url'].split('/')[-1].split('.')[0]
        item['title'] = response.xpath('//div[@class="title"]/strong/a/text()').extract()[0]
        try:
            item['author'] = response.xpath('//div[@class="au_name"]/p[2]/a/text()').extract()[0]
        except IndexError:
            item['author'] = response.xpath('//div[@id="authorWeixinContent"]/text()').extract()[0].split('：')[0][:-1]
        item['category'] = response.xpath('//div[@class="title"]/a/text()').extract()[1]
        item['sub_category'] = response.xpath('//div[@class="title"]/a/text()').extract()[2]

        item['source_id'] = 8
        item['folder_url'] = response.xpath('//div[@class="cover"]/a/img/@src').extract()[0]
        item['introduction'] = '\n'.join(response.xpath('//div[@class="info"]/p/text()').extract())
        item['status'] = 1
        item['updated_at'] = self.today
        item['created_at'] = self.today
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
        published_at = published_json['introinfo']['book']['publishtime'].split(' ')[0]
        item['published_at'] = datetime.strptime(published_at, '%Y-%m-%d')
        yield item
