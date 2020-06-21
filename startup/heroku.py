import json
import sys
from os import environ as env
from subprocess import check_call as SH

def write_config():
    j = dict(
        token=env['CONFIGJSON_TOKEN'],
        db=dict(
            dbname=env['CONFIGJSON_DBNAME'],
            user=env['CONFIGJSON_DBUSER'],
            host=env['CONFIGJSON_DBHOST'],
            password=env['CONFIGJSON_DBPASSWORD'],
            port=int(env['CONFIGJSON_DBPORT'])
        )
    )
    with open('config.json') as f:
        json.dump(j, f)

def startup_db():
    SH(['docker', 'volume', 'create', 'pgdata'])
    SH(['docker', 'run',
        '--name', 'postgres',
        '-e', f'POSTGRES_PASSWORD={env["CONFIGJSON_DBPASSWORD"]}',
        '-d',
        '-p', f'{env["CONFIGJSON_DBPORT"]}:5432',
        # '-v', 'pgdata:/var/lib/postgresql/data',
        'postgres'
    ])
    SH([sys.executable, 'startup/initdb.py'])

def startup_python():
    SH([sys.executable, '-m', 'pip', 'install', '--user', '-r', 'requirements.txt'])

def start_bot():
    SH([sys.executable, 'run.py'])

def main():
    startup_python()
    write_config()
    startup_db()
    start_bot()

if __name__ == "__main__":
    main()
