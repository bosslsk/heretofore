# -*- coding: utf-8 -*-
"""
create on 2018-01-11 下午5:42

author @heyao
"""

import os
import json
from urllib import urlencode

import requests

from hm_collections.queue.redis_queue import RedisSetQueue, RedisFifoQueue

from heretofore.sh import MonitProcess


class SpiderTaskScheduler(object):
    def __init__(self, spider_path, spider_pid_file_path, project_name='htfspider',
                short_command_format='scrapy crawl {spider_name}',
                command_format='cd {path};scrapy crawl {spider_name} &'):
        self.spider_path = spider_path
        self.spider_pid_file_path = os.path.join(spider_pid_file_path, 'spider_%(spider_name)s.pid').replace('\\', '/')
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
            try:
                pids = map(int, f.read().split(','))
            except ValueError:
                pids = []
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
        print command
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
            pids = self.schedule(spider_name, len(pids))
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


class ScrapydScheduler(object):
    """scheduler for scrapy_redis
    it use scrapyd API to deploy"""
    def __init__(self, project, server_url="http://localhost:6800"):
        self.project = project
        self.server_url = server_url

    def request(self, method, path, data=None):
        data = data or {}
        url = self.server_url + path
        if method == 'GET':
            if data:
                url += '?{0}'.format(urlencode(data))
        response = requests.request(method, url, data=data)
        content = response.content
        response.close()
        return json.loads(content)

    def schedule(self, spider_name, count=1):
        """启动一个scrapy爬虫
        :param spider_name: `scrapy.Spider.name`
        :param count: int. process count
        :return: list. pid
        """
        # requests.get(), post() scrapyd API
        if not isinstance(count, int) or count < 1:
            raise ValueError("'count' must be int and must greater than 1")
        job_ids = []
        for _ in range(count):
            data = self.request('POST', '/schedule.json', data={'project': self.project, 'spider': spider_name})
            job_ids.append(data['jobid'])
        return {'data': job_ids, 'msg': '', 'success': True}

    def pause(self, spider_name):
        """暂停一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :return:
        """
        content = self.request('GET', '/listjobs.json', data={'project': self.project})
        job_list = [
            j['id']
            for j in content['running'] + content['pending']
            if j['project'] == self.project and j['spider'] == spider_name
        ]
        for job in job_list:
            data = self.request('POST', '/cancel.json', data={'project': self.project, 'job': job})
        return {'data': {}, 'msg': '', 'success': True}

    def resume(self, spider_name, count=1):
        """重启一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :param count:
        :return:
        """
        data = self.schedule(spider_name, count)
        return data

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
        data = self.pause(spider_name)
        return data

    def kill(self, spider_name):
        """杀掉一个爬虫
        :param spider_name: `scrapy.Spider.name`
        :return:
        """
        data = self.pause(spider_name)
        return data

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
    # spider_task_scheduler = SpiderTaskScheduler()
    # print spider_task_scheduler.is_finished('qidian_index', r)
    scrapyd_scheduler = ScrapydScheduler('htf_spider')
    result = scrapyd_scheduler.schedule('qidian_index')
    print result
