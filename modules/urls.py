# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: urls.py
@time: 2020/8/9 13:31
"""

import tornado.web

from conf.config import API_VERSION

from modules import Route

from modules.service.common.handler.LoginHandler import LoginHandler


# Route mapping
Routes = [
    tornado.web.URLSpec('/api/{}/service/login'.format(API_VERSION), LoginHandler),
]


Routes.extend(Route.urls)
