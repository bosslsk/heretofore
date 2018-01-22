# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""

import os

from flask import jsonify
from flask_restful import Api
from flask_script import Shell, Server, Manager

from app import create_app, basic_auth, celery
# from .app.models import User, Role
from app.exceptions import ApiExceptions

app = create_app(os.environ.get('SPIDER_CONFIG_NAME', 'default'))
api = Api(app)

api_username = os.environ.get("SPIDER_USERNAME")
api_password = os.environ.get("SPIDER_PASSWORD")

manager = Manager(app)
server = Server(host=app.config['APP_HOST'], port=app.config['APP_PORT'])


def make_shell_context():
    return dict(app=app)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('runserver', server)


@basic_auth.get_password
def get_password(username):
    if username == api_username:
        return api_password
    return None


@app.errorhandler(ApiExceptions)
def handle_flask_error(error):
    response = jsonify(error.to_dict())
    response.msg = error.msg
    response.code = error.code
    return response


if __name__ == '__main__':
    manager.run()
