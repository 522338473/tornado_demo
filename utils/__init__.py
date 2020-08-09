# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: __init__.py.py
@time: 2020/8/9 09:39
"""

import datetime
import json
import redis
import yaml
from decimal import Decimal

from tornado.log import app_log


class Singleton(type):
    def __call__(cls, *args, **kwargs):
        if hasattr(cls, "_instance"):
            return cls._instance
        else:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls._instance


def getstore():
    from conf.config import dbConf
    from tornado_mysql import pools
    pools.DEBUG = False  # 调试模式
    return pools.Pool(dbConf['conn'], **dbConf['params'])


def getmc():
    """return Memcached ClientPool"""
    from pylibmc import Client, ClientPool
    from conf.config import cacheServers, MC_POOL_SIZE
    adv_setting = {"cas": True, "tcp_nodelay": True, "ketama": True}
    mc = Client(cacheServers, binary=False, behaviors=adv_setting)
    return ClientPool(mc, MC_POOL_SIZE)


def get_mongo():
    import motor.motor_tornado
    from conf.config import MONGO_URI
    return motor.motor_tornado.MotorClient(MONGO_URI)


def create_redis():
    from conf.config import REDIS_URI
    pool = redis.ConnectionPool.from_url(REDIS_URI,
                                         decode_responses=True)
    return redis.Redis(connection_pool=pool)


def get_aio_redis():
    import aioredis
    from conf.config import REDIS_URI
    return aioredis.create_redis_pool(REDIS_URI)


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, Decimal):
            return float(o)
        else:
            return json.JSONEncoder.default(self, o)


def module_resolver(namespace):
    namespace_parts = namespace.split(".")
    module_name = ".".join(namespace_parts[0:-1])
    cls_name = namespace_parts[-1]
    try:
        module = __import__(module_name, fromlist=["*"])
        if hasattr(module, cls_name):
            return getattr(module, cls_name)
    except Exception as ex:
        app_log.error("resolve %s failed with exception %s" % (namespace, ex))


def load_rbacfile():
    from conf.config import RBAC_FILE
    try:
        rbac_dict = yaml.safe_load(open(RBAC_FILE))
        return rbac_dict["rights"]
    except IOError as e:
        app_log.error(e)


def is_dirty(model_obj):
    obj_info = model_obj.__storm_object_info__
    return obj_info.get("sequence")

