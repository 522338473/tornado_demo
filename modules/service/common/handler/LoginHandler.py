# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: LoginHandler.py
@time: 2020/8/9 13:34
"""

from . import BaseServiceHandler


class LoginHandler(BaseServiceHandler):
    async def get(self, *args, **kwargs):
        return self.write_rows(rows='login.handler')
