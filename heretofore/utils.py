# -*- coding: utf-8 -*-
"""
create on 2018-01-25 下午3:59

author @heyao
"""

import os
import requests

usernm = os.environ.get("SPIDER_USERNAME")
passwd = os.environ.get("SPIDER_PASSWORD")


def authorized_requests(method, url, username='', password='', **kwargs):
    username = username or usernm
    password = password or passwd
    headers = kwargs.pop('headers', {})
    headers.update({'User-Agent': 'htf-slave'})
    response = requests.request(method, url, headers=headers, auth=(username, password), **kwargs)
    content = response.content
    response.close()
    return content
