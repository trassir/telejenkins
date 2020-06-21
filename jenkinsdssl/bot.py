from collections import defaultdict
import json
import logging
import os
import telegram
import telegram.utils.helpers
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, Filters, MessageHandler, TypeHandler


from jenkinsdssl.post import PostNotify, PayloadUrlButton
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


def get_chats(notifies: list):
    chats = []
    for chat_id, chat_data in database.items():
        for n in notifies:
            if n in chat_data['aliases']:
                chats.append(chat_id)
    return chats

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
        code = '\U0001f534' # red circle
    elif status == 'unstable':
        return '\U0001f7e1' # yellow circle
    elif status == 'canceled':
        return '\U0001f6c7' # crossed out circle
    return '<>'



import re
RE_ESCAPE=re.compile('([#\-_\[\]<>])')
def foobar(update: PostNotify, context: CallbackContext):
    escaper = lambda x: re.sub(RE_ESCAPE, r'\\\1', x)
    bot : telegram.Bot = context.bot
    job = escaper(update.job_name)
    build = escaper(update.build)
    url = update.build_url
    status = escaper(update.build_result)
    additional = f'\n\n{escaper(update.message)}' if update.message else ''
    icon = escaper(icon_from_status(status))

    text =f'{icon}  *__{status.upper()}__*\njob *{job}*\nbuild *{build}*' \
        f'\n[\[LINK\]]({url}){additional}'
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
    token = get_token()
    upd = Updater(token=token, use_context=True)
    disp = upd.dispatcher
    logger.info('Updater created')

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
    logger.info('Handlers set up')

    global database
    database =  defaultdict(nonedict, [(int(x),defaultdict(none, y)) for x,y in get_json(DB).items()])
    logger.info('Database acquired')
    return upd
