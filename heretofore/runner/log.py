# -*- coding: utf-8 -*-
"""
create on 2018-01-18 下午2:20

author @heyao
"""

import time
import datetime

from pymongo.errors import DuplicateKeyError


class LogSystem(object):
    def __init__(self, project, mongodb, spider_name, source_id, dt, data_coll,
                 log_coll='log', sep='_'):
        """
        :param project: project name
        :param mongodb: `pymongo.database.Database` object.
        :param spider_name: `scrapy.Spider.name`
        :param source_id: int
        :param dt: str. "yyyy-mm-dd"
        :param data_coll: 
        :param log_coll:
        :param sep: default '_'
        """
        self.project = project
        self.mongodb = mongodb
        self.spider_name = spider_name
        self.source_id = source_id
        self.dt = dt
        self.data_coll = data_coll
        self.log_coll = log_coll
        self.sep = sep

    @property
    def log_items(self):
        return [
            'project', 'name', 'date',
            'start_at', 'end_at', 'duration',
            'status', 'total_items', 'crawl_items', 'percent', 'had_run'
        ]

    @log_items.setter
    def log_items(self, items):
        raise RuntimeError("cat not set log_items")

    def init_log(self):
        _id = '{project}{sep}{name}{sep}{dt}'.format(
            project=self.project, sep=self.sep, name=self.spider_name, dt=self.dt
        )
        data = {
            '_id': _id,
            'project': self.project,
            'name': self.spider_name,
            'status': 'pending',
            'had_run': False,
            'date': datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
        }
        try:
            self.mongodb[self.log_coll].insert_one(data)
            return True
        except DuplicateKeyError:
            return False

    def _get_crawled_items(self):
        today = datetime.datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d')
        crawl_items = -1
        if self.data_coll == 'book_detail':
            crawl_items = self.mongodb['book_detail'].find({'source_id': self.source_id, 'updated_at': today}).count()
        return crawl_items

    def update_total_items(self, total_items):
        _id = '{project}{sep}{name}{sep}{dt}'.format(
            project=self.project, sep=self.sep, name=self.spider_name, dt=self.dt
        )
        self.mongodb[self.log_coll].update_one(
            {'_id': _id},
            {'$set': {'total_items': total_items}}
        )

    def run_time(self):
        # m, s = divmod(int(runtime), 60)
        # h, m = divmod(m, 60)
        # runtime = '%02dh%02dm%02ds' % (h, m, s)
        _id = '{project}{sep}{name}{sep}{dt}'.format(
            project=self.project, sep=self.sep, name=self.spider_name, dt=self.dt
        )
        log_info = self.mongodb[self.log_coll].find_one({'_id': _id})
        if not log_info:
            raise RuntimeError("please run 'init_log' first")
        if not log_info.get('had_run', False):
            return False
        if log_info['status'] == 'finished':
            return False
        dt = log_info['start_at']
        dt = dt.replace(tzinfo=None)
        runtime = int((datetime.datetime.now() - dt).total_seconds())
        crawl_items = self._get_crawled_items()
        percent = -1
        if self.data_coll == 'book_detail':
            percent = crawl_items * 1. / log_info['total_items']
        self.mongodb[self.log_coll].update_one(
            {'_id': _id},
            {'$set': {'duration': runtime, 'crawl_items': crawl_items, 'percent': int(round(percent, 3) * 1000)}}
        )
        return True

    def on_open(self):
        _id = '{project}{sep}{name}{sep}{dt}'.format(
            project=self.project, sep=self.sep, name=self.spider_name, dt=self.dt
        )
        result = self.mongodb[self.log_coll].update_one(
            {'_id': _id, 'status': 'pending'},
            {'$set': {'start_at': datetime.datetime.now(), 'status': 'running', 'had_run': True}}
        )
        return result

    def on_close(self):
        _id = '{project}{sep}{name}{sep}{dt}'.format(
            project=self.project, sep=self.sep, name=self.spider_name, dt=self.dt
        )
        self.run_time()
        result = self.mongodb[self.log_coll].update_one(
            {'_id': _id},
            {'$set': {'end_at': datetime.datetime.now(), 'status': 'finished'}}
        )
        return result
