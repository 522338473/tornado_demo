# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: auth.py
@time: 2020/8/9 12:17
"""

from tornado.concurrent import is_future
from common.core import MiddleWare


class SetDefaultHeader(MiddleWare):
    def process_request(self, request):
        request.set_header("Server", "")
        request.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
        request.set_header("Pragma", "no-cache")
        request.set_header("Expires", "0")


class CheckLogin(MiddleWare):
    async def process_request(self, handler):
        pass

    async def process_response(self, handler):
        pass


class CheckRequest(MiddleWare):
    async def process_request(self, handler):
        print(self.__dict__)


