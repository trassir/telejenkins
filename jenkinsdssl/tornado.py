
import logging
from threading import Thread

from telegram.ext import Updater
import tornado.web
from tornado.escape import json_decode
from tornado.web import url, RequestHandler
from telegram.utils.webhookhandler import WebhookServer

from jenkinsdssl.post import PostNotify

logger = logging.getLogger(__name__)

class MainHandler(RequestHandler):
    def initialize(self, upd: Updater):
        self.upd = upd

    def prepare(self):
        self.args = json_decode(self.request.body) if self.request.body else dict()
        logger.info(f'POST prepared with args {self.args}')

    def post(self):
        self.upd.update_queue.put(PostNotify(self.args))
        logger.info(f'POST sent {self.args}')


class WebhookThread(Thread):
    def __init__(self, upd: Updater):
        super().__init__()
        app = tornado.web.Application([
            url(r"/notify", MainHandler, dict(upd=upd)),
        ])
        port = 8888
        host = "0.0.0.0"
        self.webhooks = WebhookServer(host, port, app, None)
        logger.info(f'Tornado app created @ {host}:{port}')

    def run(self) -> None:
        logger.info(f'Tornado serving forever')
        self.webhooks.serve_forever()

    def shutdown(self):
        logger.info(f'Tornado shutdown')
        self.webhooks.shutdown()
