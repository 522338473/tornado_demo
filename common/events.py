# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: events.py
@time: 2020/8/9 12:12
"""

from tornado.log import app_log

from common.core import EventHub, context


class BaseWatcher(object):
    def __init__(self):
        self._evthub = EventHub()
        self.register_user_evts()

    def register_user_evts(self):
        pass

    @classmethod
    def install(watcher):
        watcher()
        app_log.debug("Event Hook [%s] install ok" % watcher)


class UserLoginWatcher(BaseWatcher):
    def register_user_evts(self):
        self._evthub.hook("user.logined", self.user_login_event)

    def user_login_event(self, user):
        app_log.debug("%s logined" % user.username)

