# -*- coding: utf-8 -*-
"""
create on 2018-01-22 上午10:28

author @heyao
"""

import time

import requests

from heretofore.runner.log import LogSystem
from heretofore.spider_settings import source_dict, data_coll_dict
from ... import celery, mongodb


def schedule_spider(method, spider_name, host='localhost'):
    path = '/api/{method}/{name}'.format(method=method, name=spider_name)
    url = 'http://{host}{path}'.format(host=host, path=path)
    headers = {'User-Agent': 'htf-slave'}
    response = requests.get(url, headers=headers)
    content = response.content
    response.close()
    return content


@celery.task
def task_schedule_spider(method, spider_name, host='localhost'):
    content = schedule_spider(method, spider_name, host)
    return content


@celery.task
def task_resume_spider_if_has_data(spider_name, host='localhost'):
    if not schedule_spider('finished', spider_name, host):
        schedule_spider('resume', spider_name, host)
        return True
    log_system = get_log_system(spider_name)
    log_system.run_time()
    log_system.on_close()
    return False


def get_log_system(spider_name, dt=None):
    dt = time.strftime('%Y-%m-%d') if dt is None else dt
    source, type = spider_name.split('_')
    source_id = source_dict[source]
    data_coll = data_coll_dict[type]
    log_system = LogSystem(
        project='htf_spider', mongodb=mongodb.db, spider_name=spider_name,
        source_id=source_id, dt=dt, data_coll=data_coll, sep='#')
    return log_system


@celery.task
def task_on_spider_open(spider_name):
    log_system = get_log_system(spider_name)
    log_system.on_open()
