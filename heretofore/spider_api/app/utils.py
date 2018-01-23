# -*- coding: utf-8 -*-
"""
create on 2017-09-06 下午3:04

author @heyao
"""

from flask import request

from app.exceptions import BadRequest


class RequestParser(object):
    def __init__(self):
        self._args = dict()

    def get_location(self, locations, help='Bad Request'):
        location_obj = None
        if isinstance(locations, str):
            locations = (locations,)
        for location in locations:
            if not hasattr(request, location):
                continue
            if not getattr(request, location):
                continue
            location_obj = getattr(request, location)
            break
        if location_obj is not None:
            return location_obj
        raise BadRequest(msg=help)

    def add_argument(self, name, type=str, required=False, help="Bad Request", location=('form', 'json'), default=None):
        """request参数验证
        :param name: 
        :param type: 
        :param required: 
        :param help: 
        :param location: str or tuple. 
        :param default: 
        :return: 
        """
        location = self.get_location(location, help)
        value = location.get(name, default)
        if required and value is None:
            raise BadRequest(msg=help)
        try:
            value = type(value)
        except TypeError:
            raise BadRequest(msg=help)
        self._args[name] = value

    def parse_args(self):
        return self._args
