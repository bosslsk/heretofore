# -*- coding: utf-8 -*-
"""
create on 2018-01-22 下午5:40

author @heyao
"""

from flask import Blueprint

trace = Blueprint('traceback', __name__)

from . import views
