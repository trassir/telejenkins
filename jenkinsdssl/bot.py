import json
import logging
import os
import re
from collections import defaultdict

import telegram
import telegram.utils.helpers
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, TypeHandler, Updater)

from jenkinsdssl.post import PayloadUrlButton, PostNotify
from jenkinsdssl.sql import sql

logger = logging.getLogger(__name__)

CONFIG = 'config.json'


REGISTER_NAME, FORGET_NAME = range(2)

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

def get_token(conf=None):
    if not conf:
        conf = get_json(CONFIG)
    c = conf.get('token')
    if not c:
        raise RuntimeError('Need "token" in config')
    return c



def start(update: Update, context: CallbackContext):
    user = update.effective_user
    description = f'{user.id}:{user.username or ""}:{user.first_name}:{user.last_name}'
    sql.set(f'''INSERT INTO chats
    (id, description) VALUES ({update.effective_chat.id}, '{description}')
    ''')
    update.message.reply_text("G'day, sire. I am Jenkins notification bot."
        f"\nThou'st registered as {description}")


def names(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user = sql.get(f'''SELECT id FROM chats
    WHERE id = {chat_id}
    ''')
    if not user:
        update.message.reply_text('Sorry, you have not registered yet')
        return
    aliases = sql.get(f'''SELECT alias FROM aliases
    WHERE chat_id = {chat_id}
    ''')
    aliases = [x[0] for x in aliases]

    if not aliases:
        update.message.reply_text('You have not created any aliases yet')
        return

    formatted = [f'`{a}`' for a in aliases]
    update.message.reply_markdown(f'You are known as:\n{", ".join(formatted)}')


def register_start(update: Update, context: CallbackContext):
    update.message.reply_text('What alias doest thou want to register with thine chat?')
    return REGISTER_NAME

def register_name(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    alias = update.message.text

    aliases = sql.get(f'''SELECT alias FROM aliases
    WHERE chat_id = {chat_id}
    ''')
    aliases = [x[0] for x in aliases] # list of tuples

    if alias in aliases:
        update.message.reply_markdown(
            f"Thou art already known as `{alias}`. Choose another or /cancel")
        return REGISTER_NAME

    aliases = sql.get(f'''SELECT alias FROM aliases
    WHERE alias = '{alias}'
    ''')
    aliases = [x[0] for x in aliases] # list of tuples
    if aliases:
        update.message.reply_markdown(
            f"Alas, m'lord, alias `{alias}` is already taken. Choose another or /cancel")
        return REGISTER_NAME

    sql.set(f'''INSERT INTO aliases
    (chat_id, alias) VALUES ({chat_id}, '{alias}')
    ''')
    update.message.reply_markdown(
        f"A'ight! Thou art known as `{update.message.text}` now.")
    return ConversationHandler.END


def forget_start(update: Update, context: CallbackContext):
    update.message.reply_text('What alias doest thou want to remove?')
    return FORGET_NAME

def forget_name(update: Update, context: CallbackContext):
    alias = update.message.text
    chat_id = update.effective_chat.id
    sql.set(f'''DELETE FROM aliases
    WHERE chat_id = {chat_id} AND alias='{alias}'
    ''')

    update.message.reply_markdown(
        "Thine name hast been forgotten.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Activity canceled')
    return ConversationHandler.END


def get_chats(notifies: list):
    aliases_wherein = ', '.join(f"'{x}'" for x in notifies)
    chats = sql.get(f'''SELECT chats.id
    FROM chats
        INNER JOIN aliases ON aliases.chat_id=chats.id
    WHERE aliases.alias IN ({aliases_wherein})
    ''')
    return [c[0] for c in chats]

def urlbuttons_from_payload(payload: list):
    buttons = []
    for p in payload:
        if isinstance(p, PayloadUrlButton):
            buttons.append(telegram.InlineKeyboardButton(text=p.name, url=p.url))
    return buttons
def icon_from_status(status: str):
    if status == 'success':
        return '\U0001f7e2' # green circle
    elif status == 'failed':
        return '\U0001f534' # red circle
    elif status == 'unstable':
        return '\U0001f7e1' # yellow circle
    elif status == 'canceled':
        return '\U0001f6c7' # crossed out circle
    return '<>'



RE_ESCAPE=re.compile('([!#\-_\[\]<>])')
def foobar(update: PostNotify, context: CallbackContext):
    escaper = lambda x: re.sub(RE_ESCAPE, r'\\\1', x)
    bot : telegram.Bot = context.bot
    url = update.build_url


    if update.type == 'simple':
        build = escaper(update.build)
        job = escaper(update.job_name)
        status = escaper(update.build_result)
        icon = f'{escaper(icon_from_status(status))}'
        additional = f'\n\n{escaper(update.message)}' if update.message else ''
        text =f'{icon}  *__{status.upper()}__*\njob *{job}*\nbuild *{build}*' \
            f'\n[\[LINK\]]({url}){additional}'
    elif update.type == 'markdown':
        text = escaper(update.markdown)
    chats = get_chats(update.notify)
    logger.info(f'Sending post data to chats: {chats}')
    for chat_id in chats:
        bot.send_message(chat_id,
        text=text,
        parse_mode=telegram.ParseMode.MARKDOWN_V2,
        reply_markup=telegram.InlineKeyboardMarkup(
            [[telegram.InlineKeyboardButton(text='JENKINS', url=url)] +
                urlbuttons_from_payload(update.payload)
            ]
        )
    )


def none(): pass
def nonedict(): return defaultdict(none,)

def init():
    config = get_json(CONFIG)

    sql.init(**config['db'])

    token = get_token(config)
    upd = Updater(token=token, use_context=True)
    disp = upd.dispatcher
    logger.info('Updater created')

    disp.add_handler(CommandHandler('start', start))
    disp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('register', register_start)],
        states={
            REGISTER_NAME: [
                MessageHandler(Filters.text & ~Filters.command, register_name)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    disp.add_handler(ConversationHandler(
        entry_points=[CommandHandler('forget', forget_start)],
        states={
            FORGET_NAME: [
                MessageHandler(Filters.text & ~Filters.command, forget_name)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    ))
    disp.add_handler(CommandHandler('names', names))
    disp.add_handler(TypeHandler(PostNotify, foobar))
    logger.info('Handlers set up')

    return upd
