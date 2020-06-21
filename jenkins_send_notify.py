#!/usr/bin/env python3

import argparse
import json
import os

import requests

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--bot_endpoint', default='http://10.16.16.67:8888/notify')
    p.add_argument('--url', default=os.getenv('BUILD_URL'))
    p.add_argument('--job', default=os.getenv('JOB_FULL_DISPLAY_NAME'))
    p.add_argument('--build', default=os.getenv('BUILD_DISPLAY_NAME'))
    p.add_argument('--notify', required=True)
    p.add_argument('--status', required=True)
    p.add_argument('--payload')
    a = p.parse_args()
    return a


def main():
    args = parse_args()
    data = dict(
        type='simple',
        job_name=args.job,
        build=args.build,
        url=args.url,
        status=args.status,
        notify=args.notify,
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
