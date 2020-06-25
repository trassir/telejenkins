import json
import sys
import urllib.parse as urlparse
from os import environ as env
from subprocess import check_call as SH

# todo: sqlalchemy?
url = urlparse.urlparse(env['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

def write_config():
    j = dict(
        token=env['CONFIGJSON_TOKEN'],
        db=dict(
            dbname=dbname,
            user=user,
            host=host,
            password=password,
            port=port,
        )
    )
    with open('config.json', 'w') as f:
        json.dump(j, f)

def startup_db():
    SH([sys.executable, 'startup/initdb.py', dbname, user, password, host, str(port)])

def start_bot():
    SH([sys.executable, 'run.py', env['PORT']])

def main():
    write_config()
    # startup_db()
    start_bot()

if __name__ == "__main__":
    main()
