# -*- coding: utf-8 -*-
"""
create on 2018-01-22 上午10:28

author @heyao
"""

import requests

from ... import celery
from heretofore.runner.log import LogSystem

log_system = LogSystem()


def schedule_spider(method, spider_name, host='localhost', port=8001):
    path = '/api/{method}/{name}'.format(method=method, name=spider_name)
    url = 'http://{host}:{port}{path}'.format(host=host, port=port, path=path)
    headers = {'User-Agent': 'htf-slave'}
    response = requests.get(url, headers=headers)
    content = response.content
    response.close()
    return content


@celery.task
def task_schedule_spider(method, spider_name, host='localhost', port=8001):
    content = schedule_spider(method, spider_name, host, port)
    return content


@celery.task
def task_resume_spider_if_has_data(spider_name, host='localhost', port=8001):
    if not schedule_spider('finished', spider_name, host, port):
        schedule_spider('resume', spider_name, host, port)
        return True
    return False


@celery.task
def task_on_spider_open(spider_name, host='localhost', port=8001):
    log_system.on_open()


@celery.task
def task_on_spider_closed(spider_name, host='localhost', port=8001):
    log_system.on_close()
