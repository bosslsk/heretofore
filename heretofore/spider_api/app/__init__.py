# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""

from celery import Celery
from flask import Flask
from flask_admin import Admin
from flask_bootstrap import Bootstrap
from flask_httpauth import HTTPBasicAuth
from flask_pymongo import PyMongo
from flask_redis import Redis

from config import config

admin = Admin(template_mode='bootstrap3')
basic_auth = HTTPBasicAuth()
bootstrap = Bootstrap()
celery = Celery(__name__)
mongodb = PyMongo()
task_redis = Redis()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    admin.init_app(app)
    bootstrap.init_app(app)
    mongodb.init_app(app, config_prefix='MONGO')
    task_redis.init_app(app, config_prefix='REDIS')

    from .main import main as main_blueprint
    from .api import api as api_blueprint
    from .traceback import trace as trace_blueprint

    app.register_blueprint(main_blueprint, url_prefix='')
    app.register_blueprint(api_blueprint, url_prefix='/api')
    app.register_blueprint(trace_blueprint, url_prefix='/traceback')

    param = app.config.iteritems()
    param = {k[0]: k[1] for k in param if not k[0].startswith('_')}
    celery.conf.update(param)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return app
