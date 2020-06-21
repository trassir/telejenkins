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
    p.add_argument('--bot_endpoint', default=os.getenv('JENKINS_TELEGRAM_ENDPOINT'))
    p.add_argument('--url', default=os.getenv('BUILD_URL'))
    p.add_argument('--job', default=os.getenv('JOB_FULL_DISPLAY_NAME'))
    p.add_argument('--build', default=os.getenv('BUILD_DISPLAY_NAME'))
    p.add_argument('--notify', required=True)
    p.add_argument('--status')
    p.add_argument('--payload')
    p.add_argument('--markdown')
    p.add_argument('--type', default='simple')
    a = p.parse_args()
    require_str(a.bot_endpoint, 'bot_endpoint')
    require_str(a.url, 'url')
    return a


def main():
    args = parse_args()
    data = dict(
        type=args.type,
        job_name=args.job,
        build=args.build,
        url=args.url,
        status=args.status,
        notify=args.notify,
        markdown=args.markdown
    )
    if args.payload:
        data['payload'] = json.loads(args.payload)
    r = requests.post(args.bot_endpoint, json.dumps(data))
    if r.status_code != 200:
        msg = json.loads(r.text) if r.headers['content-type']=='application/json' else r.text
        print(f'{r}: {r.reason}: {msg}')
        exit(1)

if __name__ == "__main__":
    main()
