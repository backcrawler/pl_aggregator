import asyncio

import sqlalchemy
from asgiref.sync import async_to_sync

from ..database import get_table, get_db_connection
from ..loggers import logger
from ..resources.fetcher import work_on_resource
from .celeryapp import celeryapp


async def async_fetch_from_resources() -> None:
    logger.warning('Ready to start async task: fetch_from_resources')  # todo: remove log
    site_t = get_table('site')
    source_t = get_table('source')
    sources_n_sites = sqlalchemy.select(source_t.c.id, source_t.c.name, source_t.c.ref).select_from(
        source_t.join(site_t, onclause=site_t.c.id == source_t.c.siteid)
        ).where(
            site_t.c.active==True
        )
    async with get_db_connection() as conn:
        result = await conn.execute(sources_n_sites)
        resources = result.fetchall()

    await asyncio.gather(*[work_on_resource(res['name'], res['ref'], res['id']) for res in resources])


@celeryapp.task(bind=True, max_retries=1, default_retry_delay=5, autoretry_for=(Exception,))
def fetch_from_resources(self) -> None:
    logger.warning('Ready to start celery task: fetch_from_resources')  # todo: remove log
    async_to_sync(async_fetch_from_resources)()
