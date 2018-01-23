# -*- coding: utf-8 -*-
"""
create on 2018-01-11 下午5:27

author @heyao
"""

# 失败了raise一个异常，然后根据异常msg，判断是否重新抓取

import json
import time
import datetime
import cPickle as pickle
from collections import Counter

from scrapy import Request
from scrapy_redis.spiders import RedisSpider
from htfspider.items import BookDetailItem


class QidianDetailSpider(RedisSpider):
    name = 'qidian_detail'
    redis_key = 'qidian:detail'
    today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')

    def make_request_from_data(self, data):
        data = pickle.loads(data)
        url = data.pop('data_url', None)
        csrf_token = data.pop('csrf_token', None)
        self.csrf_token = csrf_token
        if csrf_token is None:
            raise RuntimeError('no "csrf_token", must set')
        if url:
            req = Request(
                url,
                meta={'data': data},
                callback=self.parse,
                dont_filter=True
            )
            return req

    def str2num(self, string, cite):
        if u'万' in cite:
            return int(float(string) * 10000)
        else:
            return int(string)

    def parse_updated_at(self, updated_at):
        now = time.strftime("%Y-%m-%d")
        today_sc = int(time.mktime(time.strptime(now, "%Y-%m-%d")))
        yesterday_sc = today_sc - (60 * 60 * 24)
        tomorrow = time.strftime("%Y-%m-%d", time.localtime(int(yesterday_sc)))
        if u'今天' in updated_at:
            updated_at = now + ' ' + updated_at[2:-2] + ':00'
        elif u'昨日' in updated_at:
            updated_at = tomorrow + ' ' + updated_at[2:-2] + ':00'
        return updated_at

    def parse(self, response):
        item = BookDetailItem()
        item.update(response.meta['data'])

        update_info = response.xpath('//div[@class="book-info "]/p[last()-1]')
        # total_word = update_info.xpath('./em[1]/text()').extract()[100]
        total_word = update_info.xpath('./em[1]/text()').extract()[0]
        cite = update_info.xpath('./cite[1]/text()').extract()[0]
        item['total_word'] = self.str2num(total_word, cite)
        total_click = update_info.xpath('./em[2]/text()').extract()[0]
        cite = update_info.xpath('./cite[2]/text()').extract()[0]
        item['total_click'] = self.str2num(total_click, cite)
        total_recommend = update_info.xpath('./em[3]/text()').extract()[0]
        cite = update_info.xpath('./cite[3]/text()').extract()[0]
        item['total_recommend'] = self.str2num(total_recommend, cite)
        try:
            item['total_ticket'] = int(response.xpath('//div[@class="ticket month-ticket"]/p[2]/i/text()').extract()[0])
            item['ticket_rank'] = int(response.xpath('//div[@class="ticket month-ticket"]/p[3]/text()').extract_first('hy0')[2:])
        except (IndexError, UnicodeEncodeError):
            item['total_ticket'] = -1
            item['ticket_rank'] = -1
        try:
            item['reward'] = int(response.xpath('//div[@class="ticket"]/p[3]/em/text()').extract()[0])
        except IndexError:
            item['reward'] = 0
        item['book_status'] = (u'完本' in response.xpath('//span[@class="blue"]').extract()[0]) * 1
        book_updated_at = self.parse_updated_at(response.xpath('//em[@class="time"]/text()').extract()[0])
        item['book_updated_at'] = datetime.datetime.strptime(book_updated_at, '%Y-%m-%d %H:%M:%S')
        item['updated_at'] = self.today
        fans_url = 'https://book.qidian.com/fansrank/{0}'.format(item['book_id'])
        yield Request(
            fans_url,
            meta={'item': item},
            callback=self.parse_fans,
            dont_filter=True
        )

    def parse_fans(self, response):
        item = response.meta['item']
        fans_list = response.xpath('//div[contains(@class, "tab-cot ")]/ul/li/span[2]/text()').extract()
        counter = Counter(fans_list)
        item['fans'] = [{'name': key, 'value': counter[key]} for key in counter]
        url_format = 'https://book.qidian.com/ajax/comment/index?_csrfToken={token}&bookId={book_id}&pageSize=15'
        yield Request(
            url_format.format(token=self.csrf_token, book_id=item['book_id']),
            meta={'item': item},
            headers={'Cookie': '_csrfToken=' + self.csrf_token},
            callback=self.parse_score,
            dont_filter=True
        )

    def parse_score(self, response):
        item = response.meta['item']
        json_data = json.loads(response.body)
        item['total_score'] = json_data['data']['rate']
        item['total_scored_user'] = json_data['data']['userCount']
        url_format = 'https://book.qidian.com/ajax/book/GetBookForum?_csrfToken={token}&authorId={author_id}&bookId={book_id}&chanId={chan_id}&pageSize=15'
        yield Request(
            url_format.format(token=self.csrf_token, author_id=item['author_id'], book_id=item['book_id'], chan_id=item['chan_id']),
            meta={'item': item},
            headers={'Cookie': '_csrfToken=' + self.csrf_token},
            callback=self.parse_comment,
            dont_filter=True
        )

    def parse_comment(self, response):
        item = response.meta['item']
        item['total_comment'] = json.loads(response.body)['data']['threadCnt']
        yield item
