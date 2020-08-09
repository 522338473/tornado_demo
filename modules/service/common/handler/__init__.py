# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: __init__.py.py
@time: 2020/8/9 11:56
"""

from modules import BaseHandler

from conf.config import ENV
from common.core import context

from tornado.concurrent import is_future


class BaseServiceHandler(BaseHandler):
    """
    Base handler class for services.
    """
    @property
    def module(self):
        return "service"

    def set_default_headers(self):
        if ENV != "production":
            # Custom request header
            self.set_header("Access-Control-Allow-Origin", "*")
            self.set_header("Access-Control-Allow-Methods", "PUT, DELETE, POST, GET, OPTIONS")
            self.set_header("Access-Control-Allow-Credentials", "true")

    def options(self, *args, **kwargs):
        self.set_status(204)
        self.finish()

    async def prepare(self):
        """middleware"""
        for middleware in context['middleware']:
            res = middleware.process_request(self)
            if is_future(res):
                await res

