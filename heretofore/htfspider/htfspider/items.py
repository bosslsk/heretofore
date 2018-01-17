# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookListItem(scrapy.Item):
    source_id = scrapy.Field()
    book_id = scrapy.Field()
    url = scrapy.Field()
    published_at = scrapy.Field()  # 日期格式
    folder_url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    author_id = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    introduction = scrapy.Field()
    status = scrapy.Field()  # 书状态，默认为1，表示需要监控
    created_at = scrapy.Field()  # 创建时间
    updated_at = scrapy.Field()  # 更新时间
    chan_id = scrapy.Field()  # 讨论id


class BookDetailItem(scrapy.Item):
    source_id = scrapy.Field()
    book_id = scrapy.Field()
    url = scrapy.Field()
    published_at = scrapy.Field()  # 日期格式
    folder_url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    author_id = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    introduction = scrapy.Field()
    status = scrapy.Field()  # 书状态，默认为1，表示需要监控
    updated_at = scrapy.Field()  # 更新时间
    chan_id = scrapy.Field()

    total_word = scrapy.Field()  # 总字数
    total_click = scrapy.Field()  # 总点击，总阅读
    total_recommend = scrapy.Field()  # 总推荐，总收藏
    total_comment = scrapy.Field()  # 总评论数
    total_ticket = scrapy.Field()  # 月票数
    ticket_rank = scrapy.Field()  # 月票排行
    reward = scrapy.Field()  # 打赏，不管日打赏还是周打赏，均填入该属性
    total_score = scrapy.Field()  # 评分
    total_scored_user = scrapy.Field()  # 评分人数
    book_status = scrapy.Field()  # 书连载状态
    book_updated_at = scrapy.Field()  # 书更新时间
    fans = scrapy.Field()  # 粉丝等级数量

    # 对于历史的信息，应该有这些东西
    history_created_at = scrapy.Field()
    history_created_at_str = scrapy.Field()
