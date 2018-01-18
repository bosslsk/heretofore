# -*- coding: utf-8 -*-
"""
create on 2018-01-17 下午4:48

author @heyao
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import views
