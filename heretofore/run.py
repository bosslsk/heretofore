# -*- coding: utf-8 -*-
"""
create on 2018-01-18 下午5:51

author @heyao
"""

import time
import json
import cPickle as pickle

import redis
import pymongo
import requests
from copy import deepcopy

from hm_collections.queue.redis_queue import RedisSetQueue

from heretofore.runner.log import LogSystem
from heretofore.spider_settings import source_dict, data_coll_dict, master_host, index_start_url_dict
from heretofore.runner.scheduler import SpiderTaskScheduler
from heretofore.spider_api.app.utils import authorized_requests


def generate_id_coll(spider_name):
    source, type = spider_name.split('_')
    source_id = source_dict[source]
    data_coll = data_coll_dict[type]
    return source_id, data_coll


def collect_data(spider_name, mongodb, limit=0):
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
            i['data_url'] = 'http://app.jjwxc.org/androidapi/novelbasicinfo?novelId={}'.format(i['book_id'])
        else:
            i['data_url'] = i['url']
        if spider_name == 'qidian_detail':
            i['csrf_token'] = ''
    return data


def start_spider(redis_server, mongodb, spider_name, dt, data, host='localhost', workers=1):
    source_id, data_coll = generate_id_coll(spider_name)
    queue = RedisSetQueue(redis_server, spider_name.replace('_', ':'), pickle)
    log_system = LogSystem('htf_spider', mongodb, spider_name, source_id, dt, data_coll, sep='#')
    log_system.init_log()
    log_system.update_total_items(len(data))
    for i in data:
        queue.push(i)
    url = 'http://{host}/api/schedul/{spider}?workers={workers}'.format(
        host=host, spider=spider_name, workers=workers)
    authorized_requests('GET', url, usermame='', password='')
    return True


def get_cpu_momery_info(host, per_cpu=10, per_memory=200):
    url_cpu = 'http://{host}/api/cpu'.format(host=host)
    url_memory = 'http://{host}/api/memory'.format(host=host)
    cpu_info = json.loads(authorized_requests('GET', url_cpu, usermame='', password=''))
    memory_info = json.loads(authorized_requests('GET', url_memory, usermame='', password=''))
    cpu_data = 100 - cpu_info['data']['cpu_percent'] - 10
    memory_percent = 100 - memory_info['data']['percent'] - 10
    memory_total = memory_info['data']['total']
    memory_data = memory_total * memory_percent
    max_spider = min(int(cpu_data / per_cpu), int(memory_data / per_memory))
    return max_spider


def distribute_info(host_dict, spider_dict, mongodb):
    result = {}
    spider_data = {}
    remove_host = []
    host_dict_copyed = deepcopy(host_dict)
    for spider_name in spider_dict:
        data = generate_data(spider_name, mongodb)
        spider_data[spider_name] = data

    for spider_name in spider_data:
        for _ in range(spider_dict[spider_name]):
            for host in host_dict_copyed:
                if host in remove_host:
                    continue
                remain_times = host_dict_copyed[host]
                result[(spider_name, host)] = result.get((spider_name, host), 0) + 1
                remain_times -= 1
                host_dict_copyed[host] = remain_times
                if remain_times == 0:
                    remove_host.append(host)
    return spider_data, result


# ======================================================
# =================== workers 确定 ======================
# 1. 获取每个slave的cpu和memory信息
# 2. 根据每个爬虫占用的cpu和memory信息，估算每个slave可以运行的爬虫数量（每台slave至少保留10%的CPU和内存）
# 3. 生成运行爬虫的参数，运行爬虫


if __name__ == '__main__':
    scheduler = SpiderTaskScheduler('/Users/heyao/heretofore/heretofore/htf_spider',
                                    '/Users/heyao/heretofore/heretofore/var')
    con = pymongo.MongoClient()
    r = redis.StrictRedis()
    db = con['htf_spider']
    dt = time.strftime('%Y-%m-%d')
    limit = 30

    host_list = ['localhost', '192.168.1.18']
    spider_dict = {
        'qidian_detail': 1,
        'jjwxc_detail': 1
    }
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

        # print 'start index'
        # host = 'localhost'
        # # index_spiders = ['qidian_index', 'jjwxc_index']
        # # detail_spiders = ['qidian_detail', 'jjwxc_detail']
        # detail_spiders = ['jjwxc_detail']
        # # for index_spider in index_spiders:
        # #     start_spider(r, db, index_spider, dt, host=host, workers=4)
        # # print 'waiting'
        # # while any(not scheduler.is_finished(sp, r) for sp in index_spiders):
        # #     time.sleep(15)
        #
        # # time.sleep(120)
        # print 'start detail'
        # for detail_spider in detail_spiders:
        #     start_spider(r, db, detail_spider, dt, host=host, workers=4)
