# -*- coding: utf-8 -*-
"""
create on 2018-01-18 下午5:51

author @heyao
"""

import time
import cPickle as pickle

import redis
import pymongo
import requests

from hm_collections.queue.redis_queue import RedisSetQueue

from heretofore.runner.log import LogSystem
from heretofore.spider_settings import source_dict, data_coll_dict, master_host, index_start_url_dict
from heretofore.runner.scheduler import SpiderTaskScheduler


def generate_id_coll(spider_name):
    source, type = spider_name.split('_')
    source_id = source_dict[source]
    data_coll = data_coll_dict[type]
    return source_id, data_coll


def collect_data(spider_name, mongodb, limit=0):
    # TODO: 这里index库写死了
    source_id, data_coll = generate_id_coll(spider_name)
    param = {'_id': 0, 'status': 0, 'updated_at': 0, 'created_at': 0}
    if 'index' in data_coll:
        start_url_info = index_start_url_dict[spider_name.split('_')[0]]
        data = [
            {'data_url': start_url_info['url'].format(page=i), 'source_id': source_id}
            for i in range(1, start_url_info['total_page'] + 1)
        ]
    else:
        data = list(mongodb['book_index'].find({'source_id': source_id, 'status': 1}, param).limit(limit))
    return data


def generate_data(spider_name, mongodb, limit=0):
    source_id, data_coll = generate_id_coll(spider_name)
    data = collect_data(spider_name, mongodb, limit)
    if 'index' in data_coll:
        return data
    for i in data:
        if spider_name == 'jjwxc_detail':
            i['data_url'] = i['url']
        else:
            i['data_url'] = i['url']
        if spider_name == 'qidian_detail':
            i['csrf_token'] = ''
    return data


def start_spider(redis_server, mongodb, spider_name, dt, limit=0):
    source_id, data_coll = generate_id_coll(spider_name)
    queue = RedisSetQueue(redis_server, spider_name.replace('_', ':'), pickle)
    log_system = LogSystem('htf_spider', mongodb, spider_name, source_id, dt, data_coll, sep='#')
    log_system.init_log()
    data = generate_data(spider_name, mongodb, limit)
    log_system.update_total_items(len(data))
    for i in data:
        queue.push(i)
    url = 'http://{host}/api/schedul/{spider}?workers={workers}'.format(host=master_host, spider=spider_name, workers=4)
    requests.get(url)
    return True


scheduler = SpiderTaskScheduler('/Users/heyao/heretofore/heretofore/htf_spider', '/Users/heyao/heretofore/heretofore/var')
con = pymongo.MongoClient()
r = redis.StrictRedis()
db = con['htf_spider']
dt = time.strftime('%Y-%m-%d')
limit = 100

print 'start index'
start_spider(r, db, 'qidian_index', dt)
while not scheduler.is_finished('qidian_index', r):
    time.sleep(15)
print 'start detail'
start_spider(r, db, 'qidian_detail', dt, limit=limit)
# response = requests.get('https://book.qidian.com/info/1011093299')
# csrf_token = response.cookies.get("_csrfToken")
# print 'csrf_token:', csrf_token
