from collections import defaultdict
import json
import logging
import os
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, TypeHandler

from jenkinsdssl.post import PostNotify
logger = logging.getLogger(__name__)

CONFIG = 'config.json'
DB = 'db.json'

REGISTER_NAME, = range(1)

database = None

def get_json(filename):
    if os.path.exists(filename):
        with open(filename) as f:
            j = json.load(f)
        logger.info(f'json {filename} loaded')
    else:
        logger.info(f'json {filename} does not exist, creating anew')
        j = dict()
    return j

def dump_json(config, filename):
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    logger.info(f'json {filename} dumped')

def get_token():
    c = get_json(CONFIG).get('token')
    if not c:
        raise RuntimeError('Need "token" in config')
    return c



def start(update: Update, context: CallbackContext):
    user = update.effective_user
    description = f'{user.id}:{user.username or ""}:{user.first_name}:{user.last_name}'
    data = database[update.effective_chat.id]
    data['description'] = description
    dump_json(database, DB)
    # database[update.effective_chat.id]['description'] = description
    context.bot.send_message(chat_id=update.effective_chat.id, text=
        "G'day, sire. I am Jenkins notification bot."
        f"\nThou'st registered as {description}")


def names(update: Update, context: CallbackContext):
    user = database[update.effective_chat.id]
    if not user:
        update.message.reply_text('Sorry, you have not registered yet')
        return

    aliases = user['aliases']
    if not aliases:
        update.message.reply_text('You have not created any aliases yet')
        return

    formatted = [f'`{a}`' for a in aliases]
    update.message.reply_markdown(f'You are known as:\n{", ".join(formatted)}')


def register_start(update: Update, context: CallbackContext):
    update.message.reply_text('What alias doest thou want to register with thine chat?')
    return REGISTER_NAME

def register_name(update: Update, context: CallbackContext):
    user = database[update.effective_chat.id]
    aliases = set(user['aliases'] or [])
    aliases.add(update.message.text)
    user['aliases'] = list(aliases)
    dump_json(database, DB)

    update.message.reply_markdown(
        f"A'ight! Thou art known as `{update.message.text}` now.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Activity canceled')
    return ConversationHandler.END


def foobar(update: Update, context: CallbackContext):
    print('foobar!')


def none(): pass
def nonedict(): return defaultdict(none,)

def init():
    token = get_token()
    upd = Updater(token=token, use_context=True)
    disp = upd.dispatcher

    disp.add_handler(CommandHandler('start', start))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', register_start)],
        states={
            REGISTER_NAME: [
                MessageHandler(Filters.text & ~Filters.command, register_name)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    disp.add_handler(conv_handler)
    disp.add_handler(CommandHandler('names', names))
    disp.add_handler(TypeHandler(PostNotify, foobar))

    global database
    database =  defaultdict(nonedict, [(int(x),defaultdict(none, y)) for x,y in get_json(DB).items()])
    return upd
