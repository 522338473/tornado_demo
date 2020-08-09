# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: __init__.py.py
@time: 2020/8/9 09:38
"""

import json

import tornado.web

from conf.config import API_VERSION
from common.core import context
import utils

from tornado.concurrent import is_future


class Route(object):
    urls = []

    def __call__(self, url, name=None):
        def _(cls):
            if url.startswith("/"):
                _url = r"%s" % url
            else:
                _url = r"/api/%s/%s" % (API_VERSION, url)
            self.urls.append(tornado.web.URLSpec(_url, cls, name=name))
            return cls

        return _


Route = Route()


class BaseHandler(tornado.web.RequestHandler):
    """Tornado base handler"""

    @property
    def module(self):
        return 'main'

    def query_param_to_dict(self):
        p = {}
        for k, v in self.request.query_arguments.items():
            p[k] = str(v[0], "utf8")
        return p

    async def prepare(self):
        for middleware in context['middleware']:
            res = middleware.process_request(self)
            if is_future(res):
                await res

    def finish(self, chunk=None):
        for middleware in context["middleware"]:
            middleware.process_response(self)
        super(BaseHandler, self).finish(chunk)

    def _(self, msg):
        return self.locale.translate(msg)

    def write_rows(self, code=1, msg="", rows=()):
        if code == 1 and msg == '':
            msg = self._('success')
        elif code == -1 and msg == '':
            msg = self._('failed')
        if rows is None:
            rows = ()
        response = {"msg": msg, "code": code, "rows": rows}
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(response, cls=utils.DateEncoder))


@Route(r"/")
class IndexHandler(BaseHandler):
    def get(self):
        path = []
        base_url = "/api/{0}/{1}".format(API_VERSION, context['module'])
        for item in Route.urls:
            url = str(item.regex.pattern).replace("$", "")
            if url.startswith(base_url):
                path.append(str(item.regex.pattern).replace("$", ""))
        self.write_rows(rows={"count": len(path), "data": path})
