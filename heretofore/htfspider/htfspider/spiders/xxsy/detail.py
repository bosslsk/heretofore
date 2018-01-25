# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/24 10:55
    @subject: 潇湘书院 http://www.xxsy.net/
"""
import re
import time
import json
from collections import Counter
from datetime import datetime
import cPickle as pickle

from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from htfspider.items import BookDetailItem


class XxsyDetailSpider(RedisSpider):
    name = 'xxsy_detail'
    redis_key = 'xxsy:detail'
    today = datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

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
        item = BookDetailItem()
        item.update(response.meta['data'])
        item['book_id'] = response.url.split('/')[-1].split('.')[0]
        total_word = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()[0][:-1]
        cite = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()[0]
        item['total_word'] = self.str2num(total_word, cite)
        total_click = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()[1][:-1]
        cite = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()[1]
        item['total_click'] = self.str2num(total_click, cite)
        total_recommend = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()[2][:-1]
        cite = response.xpath('//p[@class="sub-data"]/span/em/text()').extract()[2]
        item['total_recommend'] = self.str2num(total_recommend, cite)
        item['book_status'] = (u'完' in response.xpath('//p[@class="sub-cols"]/span/text()').extract()[1]) * 1
        item['total_scored_user'] = int(response.xpath('//p[@class="appraisaled"]/text()').extract()[0][2: -3])
        item['total_score'] = float(response.xpath('//div[@id="bookstar"]/@data-score').extract()[0])
        item['reward'] = int(re.findall(r'fansCount: parseInt\((\d+)\)', response.body)[0])
        book_updated_at = response.xpath('//span[@class="time"]/text()').extract()[-1].split(' ')[0]
        item['book_updated_at'] = datetime.strptime(book_updated_at, '%Y-%m-%d')
        item['updated_at'] = self.today
        ticket_url = 'http://www.xxsy.net/info/GetBookFansInfo?bookid={}&isvip=1'.format(item['book_id'])
        yield Request(
            url=ticket_url,
            meta={'item': item},
            callback=self.parse_ticket,
            dont_filter=True
        )

    def parse_ticket(self, response):
        item = response.meta['item']
        if u'不能投月票' not in response.body:
            item['total_ticket'] = int(response.xpath('//div[@class="bd-main"]/dl/dd/p[2]/text()').extract()[0])
            ticket_rank = response.xpath('//p[@class="state"]/span/text()').extract()[0]
            item['ticket_rank'] = int(ticket_rank) if ticket_rank != '>100' else 123456
        else:
            item['total_ticket'] = -1
            item['ticket_rank'] = -1
        comment_url = 'http://www.xxsy.net/partview/GetBookReview?bookid={}&index=0&size=10&sort=1'.format(
            item['book_id'])
        yield Request(
            url=comment_url,
            meta={'item': item},
            callback=self.parse_total_comment,
            dont_filter=True
        )

    def parse_total_comment(self, response):
        item = response.meta['item']
        if u'total' in response.body:
            item['total_comment'] = int(response.xpath('//li[@id="total"]/@data-value').extract()[0])
        else:
            item['total_comment'] = -1
        fans_url = 'http://www.xxsy.net/BFnsList?bookid={}&myp=-1'.format(item['book_id'])
        yield Request(
            url=fans_url,
            meta={'item': item},
            callback=self.parse_fans,
            dont_filter=True
        )

    def parse_fans(self, response):
        item = response.meta['item']
        if u'本书还没有粉丝' in response.body:
            item['fans'] = []
            yield item
        else:
            fans_data = re.findall(r'list=\[(\{.*?\})\]', response.body)[0]
            fans_list = json.loads('[' + fans_data + ']')
            fans_nums = [fans['total'] for fans in fans_list]
            fans = [self.fans_level(fans_num) for fans_num in fans_nums]
            counter = Counter(fans)
            item['fans'] = [{'name': key, 'value': counter[key]} for key in counter]
            item['source_id'] = 6
            yield item


    def str2num(self, string, cite):
        if u'万' in cite:
            return int(float(string) * 10000)
        else:
            return int(string)

    def fans_level(self, num):
        if 0 <= num < 500:
            return u'书童'
        elif num < 2000:
            return u'童生'
        elif num < 5000:
            return u'秀才'
        elif num < 10000:
            return u'举人'
        elif num < 20000:
            return u'解元'
        elif num < 30000:
            return u'贡士'
        elif num < 40000:
            return u'会元'
        elif num < 50000:
            return u'进士'
        elif num < 70000:
            return u'探花'
        elif num < 100000:
            return u'榜眼'
        else:
            return u'状元'
