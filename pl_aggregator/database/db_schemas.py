import asyncio

import sqlalchemy
from sqlalchemy.sql.schema import Table as ITable

from .db_service import DATABASE_URL

metadata = sqlalchemy.MetaData()

site = sqlalchemy.Table(
    'site',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('baseurl', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('lang', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('active', sqlalchemy.Boolean, nullable=False, default=True),
)

source = sqlalchemy.Table(
    'source',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('ref', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('siteid', sqlalchemy.ForeignKey('site.id')),
)

post = sqlalchemy.Table(
    'post',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('tags', sqlalchemy.String),
    sqlalchemy.Column('ref', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('sourceid', sqlalchemy.ForeignKey('source.id')),
    sqlalchemy.Column('createdts', sqlalchemy.Integer, nullable=False),
    sqlalchemy.Index('post_source_idx', 'sourceid'),
    sqlalchemy.Index('post_createdts_idx', 'createdts'),
)


def get_table(name: str) -> ITable:
    return metadata.tables[name]


# todo: make migrations
async def prepare():
    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

asyncio.run(prepare())
