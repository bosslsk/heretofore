# -*- coding:utf-8 -*-
"""
    @author: harvey
    @time: 2018/1/19 17:34
    @subject: 启动爬虫
"""
import cPickle as pickle
import pprint

import pymongo
import redis

from hm_collections.queue.redis_queue import RedisSetQueue

coll = pymongo.MongoClient()['htf_spider']['book_index']


# ===============================================================
def start_jjwxc_index():
    for page in range(1, 442):
        r = redis.StrictRedis()
        queue = RedisSetQueue(r, 'jjwxc:index', serializer=pickle)
        queue.push(
            {
                'data_url': 'http://www.jjwxc.net/bookbase.php?fw0=0&fbsj=3&ycx0=0&xx0=0&sd0=0&lx0=0&fg0=0&sortType=3&isfinish=0&collectiontypes=ors&searchkeywords=&page={}'
                    .format(page)
            }
        )


def start_jjwxc_detail():
    r = redis.StrictRedis()
    queue = RedisSetQueue(r, 'jjwxc:detail', serializer=pickle)
    books = coll.aggregate([{'$project': {'book_id': 1, '_id': 0}}])
    # b = 0
    # for book in books:
    #     pprint.pprint(int(book['book_id']))
    #     b += 1
    # print b
    for book in books:
        book_id = book['book_id']
        queue.push(
            {
                'data_url': 'http://app.jjwxc.org/androidapi/novelbasicinfo?novelId={}'.format(book_id),
                'book_id': book_id
            }
        )


# ===============================================================
def start_chuangshi_index():
    for page in range(1, 1930):
        r = redis.StrictRedis()
        queue = RedisSetQueue(r, 'chuangshi:index', serializer=pickle)
        queue.push(
            {
                'data_url': 'http://chuangshi.qq.com/bk/p/{}.html'.format(page)
            }
        )


# ===============================================================
def start_yunqi_index():
    for page in range(1, 1000):
        r = redis.StrictRedis()
        queue = RedisSetQueue(r, 'yunqi:index', serializer=pickle)
        queue.push(
            {
                'data_url': 'http://yunqi.qq.com/bk/so12/n30p{}'.format(page)
            }
        )


if __name__ == '__main__':
    # start_jjwxc_index()
    # start_jjwxc_detail()
    # start_chuangshi_index()
    start_yunqi_index()
