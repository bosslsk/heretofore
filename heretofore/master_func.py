# -*- coding: utf-8 -*-
"""
create on 2018-01-18 下午5:51

author @heyao
"""

import json
import cPickle as pickle

from copy import deepcopy

from hm_collections.queue.redis_queue import RedisSetQueue

from heretofore.runner.log import LogSystem
from heretofore.spider_settings import source_dict, data_coll_dict, index_start_url_dict
from heretofore.utils import authorized_requests


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
        if spider_name in ('qidian_detail', 'qdmm_detail'):
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
    authorized_requests('GET', url, username='', password='')
    return True


def get_cpu_momery_info(host, per_cpu=10, per_memory=200):
    url_cpu = 'http://{host}/api/cpu'.format(host=host)
    url_memory = 'http://{host}/api/memory'.format(host=host)
    cpu_info = json.loads(authorized_requests('GET', url_cpu, username='', password=''))
    memory_info = json.loads(authorized_requests('GET', url_memory, username='', password=''))
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
