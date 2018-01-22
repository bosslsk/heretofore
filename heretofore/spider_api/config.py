# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""

from default_config import Config
from production_config import ProductionConfig


class DevelopmentConfig(Config):
    DEBUG = True

    # SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost:3306/love_defending'
    MONGO_HOST = 'localhost'
    MONGO_PORT = '27017'
    MONGO_DBNAME = 'love_defending'
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''

    # redis
    REDIS_URL = 'redis://localhost:6379/0'

    LOG_PATH = '/Users/heyao/spider_api.log'

    # master
    MASTER_HOST = 'localhost'

    # celery
    BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_TASK_SERIALIZER = 'json'


config = dict(
    default=DevelopmentConfig,
    development=DevelopmentConfig,
    production=ProductionConfig
)
