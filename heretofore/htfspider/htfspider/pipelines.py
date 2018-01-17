# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime

import pymongo
from scrapy.conf import settings


class HtfspiderPipeline(object):
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(settings.get("MONGO_URI"))
        db = self.client[settings.get("DB_NAME")]
        self.db = db

    def process_item(self, item, spider):
        if '_index' in spider.name:
            self.db['book_index'].update_one(
                {'_id': '%s_%s' % (item['source_id'], item['book_id'])},
                {'$setOnInsert': item},
                upsert=True
            )
        else:
            self.db['book_detail'].update_one(
                {'_id': '%s_%s' % (item['source_id'], item['book_id'])},
                {'$set': item},
                upsert=True
            )
            history_data = {}
            history_keys = [
                'total_word', 'total_click', 'total_recommend', 'book_status',
                'book_updated_at', 'book_id', 'source_id', 'total_score', 'total_scored_user',
                'total_ticket', 'ticket_rank', 'reward', 'fans', 'total_comment'
            ]
            for key in history_keys:
                history_data[key] = item[key]
            history_data['history_created_at'] = item['updated_at']
            history_data['history_created_at_str'] = item['updated_at'].strftime('%Y-%m-%d')
            history_data['_id'] = '%s_%s_%s' % (item['source_id'], item['book_id'], history_data['history_created_at_str'])
            self.db['book_detail_history'].insert_one(history_data)
        return item

    def close_spider(self, spider):
        self.client.close()
