from os import environ as env

from jenkinsdssl.sql import sql

def main():
    dbname = env['CONFIGJSON_DBNAME']
    user = env['CONFIGJSON_DBUSER']
    host = env['CONFIGJSON_DBHOST']
    password = env['CONFIGJSON_DBPASSWORD']
    port = int(env['CONFIGJSON_DBPORT'])
    sql.init(dbname=dbname, user=user, host=host, password=password, port=port)
    sql.set(f'''
DROP DATABASE "{dbname}";

CREATE DATABASE "{dbname}"
    WITH
    OWNER = "{user}"
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.utf8'
    LC_CTYPE = 'en_US.utf8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;)


CREATE TABLE public.chats
(
    id integer NOT NULL,
    description character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT chats_pkey PRIMARY KEY (id)
)
TABLESPACE pg_default;
ALTER TABLE public.chats
    OWNER to "{user}";


CREATE TABLE public.aliases
(
    chat_id integer NOT NULL,
    alias character varying COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT aliases_pkey PRIMARY KEY (alias),
    CONSTRAINT aliases_chat_id FOREIGN KEY (chat_id)
        REFERENCES public.chats (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)
TABLESPACE pg_default;
ALTER TABLE public.aliases
    OWNER to "{user}";
CREATE INDEX fki_aliases_chat_id
    ON public.aliases USING btree
    (chat_id ASC NULLS LAST)
    TABLESPACE pg_default;
''')

if __name__ == "__main__":
    main()