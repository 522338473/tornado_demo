# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: connproxy.py
@time: 2020/8/9 10:41
"""

from __future__ import absolute_import, with_statement

from common.core import context
from contextlib import contextmanager


def install_dbpool():
    from utils import getstore
    context['store'] = getstore()


def install_cache_pool():
    from utils import getmc
    context['mc'] = getmc()


def install_mongo():
    from utils import get_mongo
    context['mongo'] = get_mongo()


def get_proxy_mc():
    return context['mc']


def install_redis_pool():
    from utils import create_redis
    context["redis"] = create_redis()


def load_env():
    import os
    from dotenv import load_dotenv
    BaseDir = os.path.dirname(os.path.dirname(__file__))

    ENVDIR = os.path.join(BaseDir, '.env')
    load_dotenv(ENVDIR)


async def install_aio_redis_pool():
    from utils import get_aio_redis
    context['aio_redis'] = await get_aio_redis()


@contextmanager
def redis_cache():
    try:
        yield context["redis"]
    except:
        raise


class StoreCache(object):
    def __init__(self):
        self._store = None

    def __enter__(self):
        try:
            with context['mc'].reserve() as mc:
                self._store = mc
        except:
            raise
        return self._store

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class StoreContext(object):
    def __init__(self, dictCursor=True):
        self._store = None
        self._dictCursor = dictCursor

    def __enter__(self):
        try:
            self._store = context['store']
            if self._dictCursor:
                from tornado_mysql.cursors import DictCursor
                self._store.connect_kwargs['cursorclass'] = DictCursor
        except:
            raise
        return self._store

    def __exit__(self, exc_type, exc_value, traceback):
        pass
