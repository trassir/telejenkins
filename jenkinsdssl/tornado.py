
from threading import Thread

from telegram.ext import Updater
import tornado.web
from tornado.escape import json_decode
from tornado.web import url, RequestHandler
from telegram.utils.webhookhandler import WebhookServer

from jenkinsdssl.post import PostNotify


class MainHandler(RequestHandler):
    def initialize(self, upd: Updater):
        self.upd = upd

    def prepare(self):
        self.args = json_decode(self.request.body) if self.request.body else dict()

    def post(self):
        print(self.args)
        self.set_header('content-type', 'application/json')
        self.upd.update_queue.put(PostNotify(self.args))


class WebhookThread(Thread):
    def __init__(self, upd: Updater):
        super().__init__()
        app = tornado.web.Application([
            url(r"/notify", MainHandler, dict(upd=upd)),
        ])
        self.webhooks = WebhookServer("0.0.0.0", 8888, app, None)

    def run(self) -> None:
        self.webhooks.serve_forever()

    def shutdown(self):
        self.webhooks.shutdown()
