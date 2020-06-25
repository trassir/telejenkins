#!/usr/bin/env python3

import argparse
import json
import os

import requests
def require_str(x, name):
    if not x:
        print(f'--{name}: non-empty string is required (is env-var empty?)')
        exit(2)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--ignore_errors', action='store_true')
    p.add_argument('--bot_endpoint', default=os.getenv('JENKINS_TELEGRAM_ENDPOINT'))
    p.add_argument('--url', default=os.getenv('BUILD_URL'))
    p.add_argument('--job', default=os.getenv('JOB_FULL_DISPLAY_NAME'))
    p.add_argument('--build', default=os.getenv('BUILD_DISPLAY_NAME'))
    p.add_argument('--notify', required=True)
    p.add_argument('--status')
    p.add_argument('--text')
    p.add_argument('--payload')
    p.add_argument('--markdown')
    p.add_argument('--type', default='simple')
    a = p.parse_args()
    require_str(a.bot_endpoint, 'bot_endpoint')
    require_str(a.url, 'url')
    return a


def main():
    args = parse_args()
    if 'me' in args.notify:
        KEY = 'BUILD_USER_ID'
        author = os.getenv(KEY, '')
        print(f'JE-TL> Found "me" in notify, replacing with "{author}" from env[{KEY}]')
        args.notify = args.notify.replace('me', author)
    args.notify = args.notify.strip()
    if not args.notify:
        print(f'JE-TL> notify list is empty, skipping')
        return
    data = dict(
        type=args.type,
        job_name=args.job,
        build=args.build,
        url=args.url,
        text=args.text,
        status=args.status,
        notify=args.notify,
        markdown=args.markdown
    )
    if args.payload:
        data['payload'] = json.loads(args.payload)
    try:
        r = requests.post(args.bot_endpoint, json.dumps(data))
        if r.status_code != 200:
            msg = json.loads(r.text) if r.headers['content-type']=='application/json' else r.text
            raise RuntimeError(f'{r}: {r.reason}: {msg}')
    except Exception as e:
        print(f'JE-TL> Error: {e}')
        if not args.ignore_errors:
            return 1

if __name__ == "__main__":
    exit(main())
