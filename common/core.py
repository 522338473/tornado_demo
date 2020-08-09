# -*- coding: utf-8 -*-

"""
@author: Mr_zhang
@software: PyCharm
@file: core.py
@time: 2020/8/9 10:41
"""

import copy
import sys
import time
import weakref
from collections import defaultdict

import tornado.locale
import tornado.options
import tornado.httpserver
from tornado.ioloop import IOLoop
from tornado.log import app_log

import utils
from conf.config import settings, STATIC_PATH, TEMPLATE_PATH, LOCALES_PATH, WAITE_SECONDS_BEFORE_SHUTDOWN


class Context(metaclass=utils.Singleton):
    """A Context class used to save global information"""

    def __init__(self):
        self.store = {}

    def __setitem__(self, key, value):
        self.store[key] = value

    def __getitem__(self, key):
        return self.store[key]

    def __delitem__(self, key):
        if key in self.store:
            del self.store[key]

    def __getattr__(self, key):
        try:
            return self.store[key]
        except KeyError:
            raise AttributeError(key)

    def __contains__(self, key):
        return key in self.store

    def setdefault(self, key, value):
        if key not in self.store:
            self.store[key] = value
        return value

    def clear_keys(self, keylist):
        """It used to clear special key in self.store"""
        for key in keylist:
            if key in self.store:
                del self.store[key]

    def clear_all(self):
        """It used to clear all key in self.store"""
        keys = filter(lambda key:
                      key not in ("db", "mc") and (not key.startswith("conf.")),
                      self.store.keys()
                      )

        for key in keys:
            del self.store[key]

    def get(self, key):
        """get value for special key"""
        return self.store[key]

    def set(self, key, value):
        """set value for special key"""
        self.store[key] = value


context = Context()


class EventHub(metaclass=utils.Singleton):
    def __init__(self):
        self.evtpool = defaultdict(set)

    def emit_model_event(self, evtname, evtsrc, *data, **kwargs):
        loop = IOLoop.current()
        if "force" in kwargs or utils.is_dirty(evtsrc):
            src = utils.copy_model(evtsrc)
            if isinstance(evtname, (list, tuple)):
                for evt in evtname:
                    loop.add_callback(self.emit, evt, src, *data)
            else:
                loop.add_callback(self.emit, evtname, src, *data)

    def emit_in_loop(self, evtname, evtsrc, *data, **kwargs):
        loop = IOLoop.current()
        src = copy.deepcopy(evtsrc)
        loop.add_callback(self.emit, evtname, src, *data, **kwargs)

    def emit_system_notify(self, evtname, evtsrc):
        loop = IOLoop.current()
        src = copy.deepcopy(evtsrc)
        loop.add_callback(self.emit, evtname, src)

    def emit(self, evtname, evtsrc, *data):
        callbacks = self.evtpool[evtname]
        for callback in callbacks:
            try:
                callback(evtsrc, *data)
            except:
                app_log.exception("call callback error")

    def hook(self, evtname, callback):
        self.evtpool[evtname].add(callback)

    def unhook(self, evtname, callback):
        callbacks = self.evtpool[evtname]
        if callback in callbacks:
            callbacks.remove(callback)


EVENTBUS = EventHub()


class Application(object):
    def __init__(self):
        from tornado.options import options
        self._options = options
        self._settings = settings
        self._beforecallback = None
        self._shutdown_callback = []
        self._app = None

    def call_shutdown_callback(self):
        for callback in self._shutdown_callback:
            callback()

    def init_settings(self):
        tornado.options.parse_command_line()
        tornado.locale.set_default_locale('zh_CN')
        tornado.locale.load_gettext_translations(LOCALES_PATH, 'message')
        self._settings["debug"] = self._options.debug
        self._settings['module'] = self._options.module
        self._settings['static_path'] = STATIC_PATH,
        self._settings['template_path'] = TEMPLATE_PATH
        if not self._settings['module']:
            print("the module parameter is required.")
            exit(0)
        else:
            context['module'] = self._settings['module']
        if self._settings["debug"]:
            self._settings["autoreload"] = True
            self.install_autoreload_hook()

        if not self._options.debug:
            args = sys.argv
            args.append("--log_file_prefix=%s" % settings['logfile'])
            tornado.options.parse_command_line(args)

    @property
    def options(self):
        return self._options

    @property
    def handlers(self):
        # from urls import handlers
        from modules.urls import Routes
        return Routes

    @property
    def settings(self):
        return self._settings

    def get_app(self):
        self._beforecallback(self)
        self.init_settings()
        self.install_event_hooks()
        self.install_middleware()
        # self.install_rbac()
        self.install_message_backend()
        from tornado.web import Application
        return Application(self.handlers, **self._settings)

    def install_middleware(self):
        from conf.config import MIDDLEWARE_CLASSES
        context["middleware"] = set()
        for name in MIDDLEWARE_CLASSES:
            module = utils.module_resolver(name)
            if module:
                context["middleware"].add(module())
                app_log.debug("Middleware [%s] register ok" % name)
            else:
                app_log.error("Middleware [%s] cannot be resolved" % name)

    def install_event_hooks(self):
        from conf.config import EVENT_HOOKS
        for hook_cls in EVENT_HOOKS:
            hook = utils.module_resolver(hook_cls)
            if hook:
                hook.install()
            else:
                app_log.error("Event Hook %s cannot be resolved" % hook_cls)

    def install_rbac(self):
        rbac_dict = utils.load_rbacfile()
        context["rbac"] = rbac_dict
        app_log.debug("RBAC module register ok")

    def install_message_backend(self):
        def shutdown_message_backend():
            context.get("message_backend").close()
            del context["message_backend"]
            app_log.debug("message backend closed!")

        try:
            from conf import config
            backend_cls = utils.module_resolver(config.MESSAGE_BACKEND)
            context["message_backend"] = backend_cls(config)
            connection_future = context.get("message_backend").create_connection()
            IOLoop.current().add_future(connection_future, lambda future: future.result())
            self._shutdown_callback.append(shutdown_message_backend)
            app_log.debug("%s install ok" % config.MESSAGE_BACKEND)
        except:
            pass

    def _sig_handler(self, sig, frame):
        app_log.info("caught signal: {0}".format(sig))
        if self._settings['debug']:
            IOLoop.current().stop()
            app_log.info("Shutdown Server finally")
            return
        app_log.info("server will shutdown in {} seconds".format(WAITE_SECONDS_BEFORE_SHUTDOWN))
        self.call_shutdown_callback()
        http_server.stop()
        deadline = time.time() + WAITE_SECONDS_BEFORE_SHUTDOWN

        def stop_loop():
            now = time.time()
            if now < deadline:
                app_log.info(int(deadline - now))
                IOLoop.current().add_timeout(now + 1, stop_loop)
            else:
                IOLoop.current().stop()
                app_log.info("Shutdown Server finally")

        IOLoop.current().add_callback_from_signal(stop_loop)

    def reg_shutdown_hook(self, shutdown_handler):
        import signal
        self._shutdown_callback.append(shutdown_handler)
        signal.signal(signal.SIGTERM, self._sig_handler)
        signal.signal(signal.SIGINT, self._sig_handler)

    def before(self, before_callback):
        self._beforecallback = before_callback
        return self

    def install_autoreload_hook(self):
        if self._options.debug:
            from tornado.autoreload import add_reload_hook
            add_reload_hook(self.call_shutdown_callback)

    def start(self):
        app = self.get_app()
        global http_server
        tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOLoop')
        http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
        http_server.listen(self._options.port, address=self._options.address)
        app_log.info("server listen on %s:%d" % (self._options.address, self._options.port))
        IOLoop.current().start()


class MiddleWare(object):
    def process_request(self, handler):
        pass

    def process_response(self, handler):
        pass
