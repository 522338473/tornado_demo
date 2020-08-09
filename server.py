# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: server.py
@time: 2020/8/9 09:41
"""

from tornado.log import app_log
from tornado.options import define, options

from common.connproxy import (install_dbpool, install_cache_pool,
                              install_redis_pool, install_mongo,
                              install_aio_redis_pool, load_env)
from common.core import Application, context
from conf.config import ENV


def shutdown_handler():
    pass


def log_function(handler):
    # if "debug" in settings and settings["debug"]:
    request_time = 1000.0 * handler.request.request_time()
    try:
        if ENV == "production":
            app_log.info("%d %s %.2fms", handler.get_status(), handler._request_summary(), request_time)
        else:
            app_log.info("%d %s %.2fms %s", handler.get_status(), handler._request_summary(), request_time, str(handler.request.body, encoding="utf-8"))
    except Exception as e:
        app_log.error(e)


def set_service_status():
    pass


def before_start(app):
    load_env()
    app.reg_shutdown_hook(shutdown_handler)
    install_dbpool()
    install_cache_pool()
    # install_mongo()
    # install_redis_pool()
    set_service_status()
    from tornado import ioloop
    ioloop.IOLoop.current().spawn_callback(install_aio_redis_pool)

    app.settings["log_function"] = log_function

    from concurrent.futures.thread import ThreadPoolExecutor
    works = app.settings["executor_number"]
    app.settings["executor"] = ThreadPoolExecutor(max_workers=works)
    context["executor"] = app.settings["executor"]


def main():
    options.logging = "info"
    define("address", default='0.0.0.0', help="run server as address")
    define("port", default=8000, help="run server as port", type=int)
    define("debug", default=True, help="run as a debug model", type=bool)
    define("module", default='service', help="load specifical modules")
    Application().before(before_start).start()


if __name__ == '__main__':
    main()
