#!/usr/bin/env python3
import logging
import sys

from jenkinsdssl import bot
from jenkinsdssl import tornado

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    upd = bot.init()
    webhook_thread = tornado.WebhookThread(upd, int(sys.argv[1]))
    webhook_thread.start()
    upd.start_polling()
    upd.idle()
    webhook_thread.shutdown()

if __name__ == "__main__":
    main()
