# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: IndexHandler.py
@time: 2020/8/9 11:58
"""

from . import BaseServiceHandler
from modules import Route


@Route("service/index1")
class Index1Handler(BaseServiceHandler):

    async def get(self):
        self.write_rows(rows='')

    async def post(self):
        self.write_rows(rows='')

    async def put(self):
        self.write_rows(rows='')

    async def delete(self):
        self.write_rows(rows='')


@Route("service/index2")
class Index2Handler(BaseServiceHandler):

    async def get(self):
        self.write_rows(rows='')

    async def post(self):
        self.write_rows(rows='')

    async def put(self):
        self.write_rows(rows='')

    async def delete(self):
        self.write_rows(rows='')