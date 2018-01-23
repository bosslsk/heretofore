# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/17 16:38
    @subject: 晋江文学城 http://www.jjwxc.net
"""
import time
import json
import cPickle as pickle
from HTMLParser import HTMLParser
from datetime import datetime
from urlparse import urlparse

from scrapy import Request, FormRequest
from scrapy_redis.spiders import RedisSpider

from htfspider.items import BookListItem


class JjwxcIndexSpider(RedisSpider):
    name = 'jjwxc_index'
    redis_key = 'jjwxc:index'
    today = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def make_request_from_data(self, data):
        data = pickle.loads(data)
        url = data.pop('data_url', None)
        if url:
            req = Request(
                url,
                meta={'data': data},
                dont_filter=True
            )
            return req

    def parse(self, response):
        book_list = response.xpath('//table[@class="cytable"]/tbody/tr')[1:]
        for book in book_list:
            item = BookListItem()
            href = book.xpath('./td/a/@href').extract()[1]
            item['book_id'] = urlparse(href).query.split('=')[1]
            try:
                published_at = book.xpath('./td/text()').extract()[-1].split(' ')[0]
            except IndexError as e:
                self.logger.debug('no publish time: %s' % item['book_id'])
                continue
            item['published_at'] = datetime.strptime(published_at, '%Y-%m-%d')
            book_url = 'http://app.jjwxc.org/androidapi/novelbasicinfo?novelId={}'.format(item['book_id'])
            yield FormRequest(
                book_url,
                formdata={'versionCode': '75'},
                meta={'item': item},
                callback=self.parse_detail,
                dont_filter=True
            )

    def parse_detail(self, response):
        item = response.meta['item']
        detail_json = json.loads(response.body)
        clock = int(detail_json['islock'])
        if clock == 1:
            self.logger.debug('[THIS BOOK IS CLOCK] ' + response.url)
            return
        sign = int(detail_json['isSign'])
        if sign == 0:
            self.logger.debug('[NOT SIGN] ' + response.url)
            return
        item['source_id'] = 7
        item['url'] = 'http://www.jjwxc.net/onebook.php?novelid={}'.format(item['book_id'])
        item['folder_url'] = detail_json['novelCover']
        item['title'] = detail_json['novelName']
        item['author'] = detail_json['authorName']
        item['author_id'] = detail_json['authorId']
        if detail_json['novelClass'] == '':
            item['category'] = ''
            item['sub_category'] = ''
        else:
            item['category'] = detail_json['novelClass']
            item['sub_category'] = ''  # detail_json['novelClass'].split('-')[-1]
        introduction = HTMLParser().unescape(detail_json['novelIntro'])
        item['introduction'] = '\n'.join(p.strip() for p in introduction.split('<br/>') if p != '')
        item['status'] = 1
        item['created_at'] = self.today
        item['updated_at'] = self.today
        yield item
