from collections import defaultdict
import json
import logging
import os

from telegram.ext import Updater
from telegram.ext import CommandHandler, TypeHandler

CONFIG = 'config.json'
from jenkinsdssl.post import PostNotify

def get_config():
    if os.path.exists(CONFIG):
        with open(CONFIG) as f:
            j = json.load(f)
    else:
        j = dict()
        dump_json(j, CONFIG)
    return defaultdict(lambda: None, j)

def dump_json(config, filename):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)


def get_token():
    j = get_config()
    c = j['token']
    if not c:
        dump_json(j, CONFIG)
        raise RuntimeError('Need "token" in config')
    return c

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

_token=None
upd=None

def foobar(update, context):
    print('foobar!')

def token():
    return _token

def init():
    global _token
    _token = get_token()
    global upd
    upd = Updater(token=_token, use_context=True)
    disp = upd.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    disp.add_handler(CommandHandler('start', start))
    disp.add_handler(TypeHandler(PostNotify, foobar))
    return upd

def run():
    upd.start_polling()
    upd.update_queue.put(MyUpdate(post_data, post_something))
