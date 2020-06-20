#!/usr/bin/env python3
from jenkinsdssl import bot
from jenkinsdssl import tornado

def main():
    upd = bot.init()
    webhook_thread = tornado.WebhookThread(upd)
    webhook_thread.start()
    upd.start_polling()
    upd.idle()
    webhook_thread.shutdown()

if __name__ == "__main__":
    main()
