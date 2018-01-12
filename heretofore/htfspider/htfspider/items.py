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
    published_at = scrapy.Field()
    folder_url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    introduction = scrapy.Field()
