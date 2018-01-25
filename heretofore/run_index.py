# -*- coding: utf-8 -*-
"""
create on 2018-01-24 下午8:40

author @heyao
"""

import time

import pymongo
import redis

from heretofore.master_func import get_cpu_momery_info, distribute_info, start_spider
from heretofore.spider_settings import mongo_uri, redis_uri, mongo_auth, host_list, index_spider_dict as spider_dict

con = pymongo.MongoClient(mongo_uri)
r = redis.StrictRedis.from_url(redis_uri)
db = con['htf_spider']
if mongo_auth:
    db.authenticate(**mongo_auth)

dt = time.strftime('%Y-%m-%d')

data = {}
for host in host_list:
    max_spider_num = get_cpu_momery_info(host, per_cpu=10, per_memory=200)
    data[host] = max_spider_num
spider_data, dis_dict = distribute_info(data, spider_dict, db)
for spider, host in dis_dict:
    workers = dis_dict[(spider, host)]
    total_items = len(spider_data[spider])
    print 'schdule', spider, 'on', host, 'for', workers, 'times with', total_items, 'item'
    start_spider(r, db, spider, dt, spider_data[spider], host, workers)
