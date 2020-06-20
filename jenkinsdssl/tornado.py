import json
import logging
from threading import Thread

from telegram.ext import Updater
import tornado.web as tw
from telegram.utils.webhookhandler import WebhookServer

from jenkinsdssl.post import PostNotify

logger = logging.getLogger(__name__)

class MainHandler(tw.RequestHandler):
    def initialize(self, upd: Updater):
        self.upd = upd

    def prepare(self):
        self.args = json.loads(self.request.body) if self.request.body else dict()
        logger.info(f'POST prepared with args {self.args}')

    def post(self):
        self.set_header('content-type', 'application/json')
        try:
            try:
                p = PostNotify(**self.args)
            except ValueError as e:
                logger.info(f'Could not construct PostNotify: {e}')
                self.set_status(400)
                self.finish(json.dumps(dict(error=f'Bad arguments: {e}')))
                return
            self.upd.update_queue.put(p)
            logger.info(f'POST data enqueued as {json.dumps(p, default=lambda x: x.__dict__)}')
        except Exception as e:
            logger.error(e)
            self.set_status(500)
            self.finish(json.dumps(dict(error=f'Some internal server error: {e}')))


class WebhookThread(Thread):
    def __init__(self, upd: Updater):
        super().__init__()
        app = tw.Application([
            tw.url(r"/notify", MainHandler, dict(upd=upd)),
        ])
        port = 8888
        host = "0.0.0.0"
        self.webhooks = WebhookServer(host, port, app, None)
        logger.info(f'Tornado app created @ {host}:{port}')

    def run(self):
        logger.info(f'Tornado serving forever')
        self.webhooks.serve_forever()

    def shutdown(self):
        logger.info(f'Tornado shutdown')
        self.webhooks.shutdown()
