# -*- coding: utf-8 -*-
"""
create on 2018-01-22 下午3:38

author @heyao
"""

source_dict = {
    'qidian': 1,
    'zh': 2,
    'xx': 6,
    'jjwxc': 7,
    'cs': 8,
    'yq': 11,
    'qdmm': 21
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
    'jjwxc': {}
}
