# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""
import datetime

from flask import jsonify, request, current_app

from app import basic_auth, mongodb
from app.exceptions import ApiExceptions, UNAUTHORIZED, INTERNAL_SERVER_ERROR
from . import api
from .. import task_redis
from ..tasks.http.slave import task_schedule_spider, task_resume_spider_if_has_data, task_on_spider_open
from ..utils import RequestParser


@basic_auth.error_handler
def unauthorized():
    raise ApiExceptions(code=UNAUTHORIZED, msg='Unauthorized')


@api.route('/')
@basic_auth.login_required
def index():
    return jsonify(code=200, msg="I'm alive", data={'host': dict(request.headers)})


@api.route('/schedul/<spider_name>')
@basic_auth.login_required
def schedul(spider_name):
    workers = request.args.get('workers', 1)
    try:
        workers = int(workers)
    except ValueError as e:
        raise ApiExceptions(INTERNAL_SERVER_ERROR, msg=e.message)
    current_app.scheduler.schedule(spider_name, workers)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/pause/<spider_name>')
@basic_auth.login_required
def pause(spider_name):
    current_app.scheduler.pause(spider_name)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/resume/<spider_name>')
# @basic_auth.login_required
def resume(spider_name):
    current_app.scheduler.resume(spider_name)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/stop/<spider_name>')
@basic_auth.login_required
def stop(spider_name):
    force = request.args.get('force', 0)
    try:
        force = int(force)
    except ValueError as e:
        raise ApiExceptions(INTERNAL_SERVER_ERROR, msg=e.message)
    current_app.scheduler.stop(spider_name, task_redis, force)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/finished/<spider_name>')
@basic_auth.login_required
def is_finished(spider_name):
    b = current_app.scheduler.is_finished(spider_name, task_redis)
    return jsonify(code=200, msg='SUCCESS', data={'finished': b})


@api.route('/memory')
@basic_auth.login_required
def memory():
    """内容使用情况
    :return: 
    """
    memory_info = current_app.monitor_process.memory_state()
    keys = ['total', 'free', 'available', 'used', 'active', 'inactive']
    percent = memory_info.percent
    memory_info = {k: round(getattr(memory_info, k) * 1. / 1024 / 1024, 2) for k in keys}
    memory_info['percent'] = percent
    return jsonify(code=200, msg='SUCCESS', data=dict(**memory_info))


@api.route('/cpu')
@basic_auth.login_required
def cpu():
    cpu_info = current_app.monitor_process.cup_state(3)
    return jsonify(code=200, msg='SUCCESS', data=dict(cpu_percent=cpu_info))


# ======== master ========
@api.route('/ready/stop/<spider_name>')
@basic_auth.login_required
def ready_stop(spider_name):
    host = request.headers.get("X-Forwarded-For")
    task_schedule_spider.delay('pause', spider_name, host)
    dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
    task_resume_spider_if_has_data.apply_async((spider_name, host), eta=dt)
    return jsonify(code=200, msg='SUCCESS', data={})


@api.route('/ready/start/<spider_name>')
# @basic_auth.login_required
def ready_start(spider_name):
    task_on_spider_open.delay(spider_name)
    return jsonify(code=200, msg='SUCCESS', data=None)


@api.route('/traceback/save/<spider_name>', methods=['POST'])
@basic_auth.login_required
def traceback_save(spider_name):
    request_parser = RequestParser()
    request_parser.add_argument('data', type=dict, required=True, location=('json',))
    args = request_parser.parse_args()
    data = args['data']
    data['created_at'] = datetime.datetime.now()
    data['spider'] = spider_name
    mongodb.db['traceback'].insert(data)
    return jsonify(code=200, msg='SUCCESS', data=None)
