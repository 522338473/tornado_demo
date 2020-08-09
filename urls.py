# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: urls.py
@time: 2020/8/9 11:25
"""

import os

from common.core import context

module = context['module'].split(",")
module = [m for m in module]

handlers = []

# 检查输入的模块是否存在
file_path = os.path.join(os.path.abspath(os.path.curdir), 'modules')
module = [m for m in module if os.path.exists(os.path.join(file_path, m))]

if module:
    from modules import Route
    # from modules.urls import Routes
    __import__("modules", fromlist=module)
    for url in Route.urls:
        if any([url.regex.pattern.count(m) for m in module]) or url.regex.pattern == "/$":
            handlers.append(url)
else:
    exit('not found module')