# -*- coding: utf-8 -*-
"""
create on 2018-01-07 下午9:41

author @heyao
"""

import os


class Config(object):
    APP_HOST = '0.0.0.0'
    APP_PORT = 8001
    SECRET_KEY = os.environ.get("SPIDER_SECRET_KEY")
    # SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass
