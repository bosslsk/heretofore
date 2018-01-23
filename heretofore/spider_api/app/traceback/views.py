# -*- coding: utf-8 -*-
"""
create on 2018-01-22 下午5:40

author @heyao
"""
import math

from bson import ObjectId
from flask import render_template, flash, redirect, url_for, jsonify

from . import trace
from .. import mongodb


class Pagination(object):
    def add_arg(self, name, value):
        setattr(self, name, value)


def generate_pagination(data, page, pagesize=6):
    total_items = data.count()
    data = data.skip((page - 1) * pagesize).limit(pagesize)
    data = list(data)
    pages = int(math.ceil(total_items * 1. / pagesize))

    def get_info():
        max_page = pages + 1
        for i in range(max(1, page - 4), min(max_page, max(1, page - 4) + 10)):
            yield i

    pagination = Pagination()
    pagination.add_arg('has_prev', page != 1)
    pagination.add_arg('page', page)
    pagination.add_arg('iter_pages', get_info)
    pagination.add_arg('has_next', (total_items / pagesize) > page)
    pagination.add_arg('pages', pages)
    return pagination, data


@trace.route('/<page>')
def trace_spider(page):
    page = int(page)
    pagesize = 6
    tracebacks = mongodb.db['traceback'].find({'status': {'$ne': 1}, 'error_type': 1}).sort([('created_at', -1), ('status', 1)])
    pagination, tracebacks = generate_pagination(tracebacks, page, pagesize)
    for traceback in tracebacks:
        traceback['error'] = traceback['error'].split('\n')
    return render_template('traceback/list.html', tracebacks=tracebacks, pagination=pagination)


@trace.route('/mark/<tid>/<status>')
def trace_mark(tid, status=1):
    status = int(status)
    if status != 0 and status != 1:
        return jsonify(code=400, msg='ERROR', data=None)
    _id = ObjectId(tid)
    mongodb.db['traceback'].update_one({'_id': _id}, {'$set': {'status': status}})
    return jsonify(code=200, msg='SUCCESS', data=None)
