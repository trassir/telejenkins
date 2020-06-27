import logging
import sqlalchemy as db

logger = logging.getLogger(__name__)

class sql:
    _connection = None

    chats = None
    aliases = None
    @staticmethod
    def init(**kwargs):
        from collections import namedtuple
        S = namedtuple('S', 'dbname user host password port')
        d = S(**kwargs)

        engine = db.create_engine(f'postgres://{d.user}:{d.password}@{d.host}:{d.port}/{d.dbname}')
        metadata = db.MetaData()
        sql._connection = engine.connect()

        sql.chats = db.Table('chats', metadata,
            db.Column('id', db.Integer(), primary_key=True),
            db.Column('description', db.VARCHAR()),
        )
        sql.aliases = db.Table('aliases', metadata,
            db.Column('chat_id', db.Integer(), db.ForeignKey("chats.id"),),
            db.Column('alias', db.VARCHAR(), primary_key=True),
        )
        metadata.create_all(engine) #Creates the table

    @staticmethod
    def get(query):
        logger.info(f'.get:\n{query}')
        return sql._connection.execute(query).fetchall()
    @staticmethod
    def set(query):
        logger.info(f'.set:\n{query}')
        return sql._connection.execute(query)
