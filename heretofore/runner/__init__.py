# -*- coding: utf-8 -*-
"""
create on 2018-01-11 下午5:12

author @heyao
"""

import os

import time

from heretofore import base_dir
from heretofore.runner.runner_settings import spider_pid_file_path
from heretofore.runner.scheduler import SpiderTaskScheduler


class Runner(object):
    def __init__(self, index_spiders=(), detail_spiders=()):
        self.index_spiders = index_spiders
        self.detail_spiders = detail_spiders

    def run_index_spider(self):
        """运行索引信息的爬虫
        :return: 
        """
        if not self.index_spiders:
            return False
        spider_path = os.path.join(base_dir, 'htfspider')
        spider_task_schduler = SpiderTaskScheduler(spider_path, spider_pid_file_path)

        for spider in self.index_spiders:
            spider_task_schduler.schedule(spider, 4)
        return True

    def run_detail_spider(self, redis_server):
        """运行详细信息的爬虫
        process: 
        1. 等待所有的index队列完毕，item也处理完毕
        2. 关掉所有的index爬虫
        3. 启动detail爬虫
        :param redis_server: 
        :return: 
        """
        if not self.detail_spiders:
            return False
        spider_path = os.path.join(base_dir, 'htfspider')
        spider_task_monitor = SpiderTaskScheduler(spider_path, spider_pid_file_path)

        while any(not spider_task_monitor.is_finished(spider_name, redis_server) for spider_name in index_spiders):
            # TODO: 或许有更好的方式？
            time.sleep(5)

        for spider_name in self.index_spiders:
            spider_task_monitor.stop(spider_name, redis_server, force_stop=True)

        # run detail spiders
        for spider_name in self.detail_spiders:
            spider_task_monitor.schedule(spider_name)
        return True
