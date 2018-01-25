# -*- coding: utf-8 -*-
"""
create on 2018-01-22 下午3:38

author @heyao
"""

source_dict = {
    'qidian': 1,
    'xxsy': 6,
    'jjwxc': 7,
    'yunqi': 11,
    'qdmm': 21,
    'chuangshi': 8
}

data_coll_dict = {
    'index': 'book_index',
    'detail': 'book_detail'
}

master_host = 'localhost'

index_start_url_dict = {
    'qidian': {
        'url': 'https://www.qidian.com/all?orderId=5&style=1&pageSize=20&siteid=1&pubflag=0&hiddenField=0&page={page}',
        'total_page': 800
    },
    'qdmm': {
        'url': 'https://www.qidian.com/mm/all?orderId=5&style=1&pageSize=20&siteid=0&pubflag=0&hiddenField=0&page={page}',
        'total_page': 300
    },
    'jjwxc': {
        'url': 'http://www.jjwxc.net/bookbase.php?fw0=0&fbsj=0&ycx0=0&xx0=0&mainview0=0&sd0=0&lx0=0&fg0=0&sortType=1&isfinish=0&collectiontypes=ors&searchkeywords=&page={page}',
        'total_page': 100
    },
    'chuangshi': {
        'url': 'http://chuangshi.qq.com/bk/so2/p/{page}.html',
        'total_page': 70
    }
}

host_list = ['localhost', '127.0.0.1']

index_spider_dict = {
    'qidian_index': 1,
    'qdmm_index': 1,
    # 'xxsy_index': 1,
    'jjwxc_index': 1,
    'chuangshi_index': 1,
    # 'yunqi_index': 1
}

detail_spider_dict = {
    'qidian_detail': 1,
    'qdmm_detail': 1,
    # 'xxsy_detail': 1,
    'jjwxc_detail': 1,
    'chuangshi_detail': 1,
    # 'yunqi_detail': 1
}

mongo_uri = 'mongodb://localhost:27017'
db_name = 'htf_spider'
mongo_auth = {}
redis_uri = 'redis://localhost:6379'

try:
    from product_spider_settings import *
except ImportError:
    pass
