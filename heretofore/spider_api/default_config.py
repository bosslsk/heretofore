# -*- coding: utf-8 -*-
"""
create on 2018-01-07 下午9:41

author @heyao
"""

import os
from heretofore.runner.scheduler import SpiderTaskScheduler
from heretofore.sh import MonitProcess


class Config(object):
    APP_HOST = '0.0.0.0'
    APP_PORT = 8001
    SECRET_KEY = os.environ.get("SPIDER_SECRET_KEY")

    # SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        app.scheduler = SpiderTaskScheduler(spider_path=app.config['SPIDER_PATH'],
                                            spider_pid_file_path=app.config['SPIDER_PID_FILE_PATH'])
        app.monitor_process = MonitProcess()
