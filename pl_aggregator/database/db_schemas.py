import sqlalchemy

from .db_service import DATABASE_URL

metadata = sqlalchemy.MetaData()

post = sqlalchemy.Table(
    'post',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('tags', sqlalchemy.String),
    sqlalchemy.Column('ref', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('source', sqlalchemy.ForeignKey('site.id')),
    sqlalchemy.Column('createdts', sqlalchemy.Integer, nullable=False),
    sqlalchemy.Index('post_source_idx', 'source'),
    sqlalchemy.Index('post_createdts_idx', 'createdts'),
)

site = sqlalchemy.Table(
    'site',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('ref', sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column('lang', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('active', sqlalchemy.Boolean, nullable=False, default=True),
)


async def prepare():
    from sqlalchemy.ext.asyncio import create_async_engine
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

import asyncio
asyncio.run(prepare())
