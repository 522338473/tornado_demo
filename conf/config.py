# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: config.py
@time: 2020/8/9 11:01
"""

import os
import yaml


ENV = 'production'  # 'dev', 'production', testing

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates")  # 模版目录
STATIC_PATH = os.path.join(BASE_DIR, "static")  # 静态资源目录
CONF_PATH = os.path.join(BASE_DIR, 'conf')
LOCALES_PATH = os.path.join(BASE_DIR, "locales")

_CFG = yaml.safe_load(open(os.path.join(CONF_PATH, "conf.yml")))

API_VERSION = 'v1'
PROTOCOL_TYPE = 'http'  # http https

if ENV == "dev":
    cfg = _CFG["dev"]
elif ENV == "production":
    cfg = _CFG["production"]
elif ENV == _CFG["testing"]:
    cfg = _CFG["testing"]
else:
    raise Exception("ENV flag error")

WAITE_SECONDS_BEFORE_SHUTDOWN = cfg["shutdown_wait_seconds"]

dbConf = {
    "conn": {
        "host": cfg['mysql']['host'],
        "port": cfg['mysql']['port'],
        "db": cfg['mysql']['db'],
        "user": cfg['mysql']['user'],
        "password": cfg['mysql']['password'],
        "charset": "utf8",
    },
    "params": {  # 连接池参数
        "max_idle_connections": 20,  # 最大保持连接数
        "max_recycle_sec": 3600,  # 回收时间
    }
}

cacheServers = [cfg['memcached']['host']]
MC_POOL_SIZE = 100

MONGO_URI = cfg['mongo']['uri']
REDIS_URI = cfg['redis']['uri']
REDIS_HOST = cfg['redis']['host']
MQ_URI = "amqp://rabbitmq:rabbitmq123456@rabbitmq:5672//"


def get_protocol():
    if PROTOCOL_TYPE == 'http':
        return 'http://'
    elif PROTOCOL_TYPE == 'https':
        return 'https://'
    else:
        raise Exception('protocol type error')


EVENT_HOOKS = (
    "common.events.UserLoginWatcher",
)

MIDDLEWARE_CLASSES = (
    # "common.auth.CheckLogin",
    "common.auth.CheckRequest",
    "common.auth.SetDefaultHeader",
)

settings = {
    "gzip": True,
    "salt": cfg['secret']['salt'],
    "token_duration": 3600,
    "token_name": "X-Xsrf-Token",
    "timestamp": "T",  # http header 请求时间戳
    "signature": "Sign",
    "auth_cookie_name": "Cookie-Token-{}",  # format use module name.
    "cookie_secret": cfg['secret']['cookie_secret'],
    "executor_number": 20
}
