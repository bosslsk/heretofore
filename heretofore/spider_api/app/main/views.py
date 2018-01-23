# -*- coding: utf-8 -*-
"""
create on 2018-01-22 下午6:58

author @heyao
"""

import datetime

from flask import render_template, jsonify

from app import mongodb
from . import main
from app.tasks.http.slave import get_log_system


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/report/date')
def report_date():
    dates = sorted(set([i['date'].strftime('%Y-%m-%d') for i in mongodb.db['log'].find()]), reverse=True)
    return jsonify(code=200, msg='SUCCESS', data={'dates': dates, 'recent': dates[0]})


@main.route('/report/<date>')
def report(date):
    logs = list(mongodb.db['log'].find({'date': datetime.datetime.strptime(date, '%Y-%m-%d')}))
    dates = sorted(set([i['date'].strftime('%Y-%m-%d') for i in mongodb.db['log'].find()]), reverse=True)
    for log in logs:
        log_system = get_log_system(log['name'], date)
        log_system.run_time()
    return render_template('report/current.html', logs=logs, dates=dates, current=date)


@main.route('/report/jump')
def report_jump():
    return render_template('report/jump.html')
