# -*- coding: utf-8 -*-
"""
create on 2018-01-11 下午5:42

author @heyao
"""

import os

from hm_collections.queue.redis_queue import RedisSetQueue, RedisFifoQueue

from heretofore.sh import MonitProcess


class SpiderTaskScheduler(object):
    def __init__(self, spider_path, spider_pid_file_path, project_name='htfspider',
                short_command_format='scrapy crawl {spider_name}',
                command_format='cd {path};scrapy crawl {spider_name} & >> /Users/heyao/Desktop/heretofore/{spider_name}.log 2>&1'):
        self.spider_path = spider_path
        self.spider_pid_file_path = spider_pid_file_path
        self.project_name = project_name
        self.short_command_format = short_command_format
        self.command_format = command_format
        self.process_monitor = MonitProcess()

    def _clear_pid_file(self, pid_path):
        with open(pid_path, 'w') as f:
            f.write('')

    def _write_pid(self, pids, pid_path):
        with open(pid_path, 'w') as f:
            f.write(','.join(map(str, pids)))

    def _read_pid(self, pid_path):
        with open(pid_path, 'r') as f:
            pids = map(int, f.read().split(','))
        return pids

    def schedule(self, spider_name, count=1):
        """启动一个scrapy爬虫
        :param spider_name: `scrapy.Spider.name`
        :param count: int. process count
        :return: list. pid
        """
        if not isinstance(count, int) or count < 1:
            raise ValueError("'count' must be int and must greater than 1")
        command = self.command_format.format(path=self.spider_path, spider_name=spider_name)
        for _ in range(count):
            os.system(command)
        short_command = self.short_command_format.format(spider_name=spider_name)
        pids = self.process_monitor.get_pids(short_command)
        self._write_pid(pids, self.spider_pid_file_path % dict(spider_name=spider_name))
        return pids

    def pause(self, spider_name):
        """暂停一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :return: 
        """
        pids = self._read_pid(self.spider_pid_file_path % dict(spider_name=spider_name))
        self.process_monitor.send_signal(pids, 'SIGINT')
        return pids

    def resume(self, spider_name):
        """重启一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :return: 
        """
        pids = self._read_pid(self.spider_pid_file_path % dict(spider_name=spider_name))
        if pids:
            command = self.command_format.format(path=self.spider_path, spider_name=spider_name)
            os.system(command)
        return pids

    def stop(self, spider_name, redis_server, force_stop=False):
        """停止一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :param redis_server: `redis.StrictRedis`
        :param force_stop: default False, if True, it will flush data, then send a SIGINT signal.
        :return: 
        """
        if not self.is_finished(spider_name, redis_server):
            if force_stop:
                self.flush(spider_name, redis_server)
            else:
                return False
        pid_path = self.spider_pid_file_path % dict(spider_name=spider_name)
        pids = self._read_pid(pid_path)
        self.process_monitor.send_signal(pids, 'SIGINT')
        self._clear_pid_file(pid_path)
        return pids

    def kill(self, spider_name):
        """杀掉一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :return: 
        """
        pids = self._read_pid(self.spider_pid_file_path % dict(spider_name=spider_name))
        self.process_monitor.send_signal(pids, 'SIGKILL')
        self._clear_pid_file(spider_name)
        return pids

    def is_finished(self, spider_name, redis_server):
        """判断一个爬虫是否进行完毕
        包括：起始队列，存放items的队列，存放requests的队列 
        :param spider_name: `scrapy.Spider.name`
        :param redis_server: `redis.StrictRedis`
        :return: bool.
        """
        # start_urls queue
        queue = RedisSetQueue(redis_server, spider_name.replace('_', ':'))
        if len(queue):
            return False
        # items queue
        queue = RedisFifoQueue(redis_server, spider_name + ':items')
        if len(queue):
            return False
        # requests queue
        queue = RedisFifoQueue(redis_server, spider_name + ':requests')
        if len(queue):
            return False
        return True

    def flush(self, spider_name, redis_server):
        queue = RedisSetQueue(redis_server, spider_name.replace('_', ':'))
        queue.flush()
        queue = RedisFifoQueue(redis_server, spider_name + ':items')
        queue.flush()
        queue = RedisFifoQueue(redis_server, spider_name + ':requests')
        queue.flush()


if __name__ == '__main__':
    import redis

    r = redis.StrictRedis()
    spider_task_scheduler = SpiderTaskScheduler()
    print spider_task_scheduler.is_finished('qidian_index', r)
