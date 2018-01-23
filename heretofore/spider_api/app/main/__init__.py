# -*- coding: utf-8 -*-
"""
create on 2018-01-22 下午6:58

author @heyao
"""

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
