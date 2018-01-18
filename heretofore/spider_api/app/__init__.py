# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""

from flask import Flask
from flask_httpauth import HTTPBasicAuth

from flask_pymongo import PyMongo
from flask_redis import Redis

from config import config

basic_auth = HTTPBasicAuth()
mongodb = PyMongo()
task_redis = Redis()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mongodb.init_app(app, config_prefix='MONGO')
    task_redis.init_app(app, config_prefix='REDIS')

    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
