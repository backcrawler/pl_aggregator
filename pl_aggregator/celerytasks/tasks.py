import asyncio
import time
from datetime import timedelta

import sqlalchemy
from asgiref.sync import async_to_sync
import celery
from celery.schedules import crontab

from ..database import get_table, get_db_connection
from ..configs import get_settings
from ..loggers import logger
from ..resources.fetcher import work_on_resource
from .celeryapp import celeryapp

settings = get_settings()


@celeryapp.on_after_configure.connect
def setup_periodic_tasks(sender: celery.app.base.Celery, **kwargs):
    # Executes every 5 minutes
    sender.add_periodic_task(60*5, fetch_from_resources.s(), name='fetch_from_resources_cron')

    # Executes every morning at 6:30 a.m.
    sender.add_periodic_task(
        crontab(hour=6, minute=30),
        clear_expired_rows.s(),
    )


async def async_fetch_from_resources() -> None:
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


async def async_clear_expired_rows() -> int:
    post_t = get_table('post')
    total_secs = timedelta(days=settings.post_days_ttl).total_seconds()
    del_query = sqlalchemy.delete(post_t).where(post_t.c.createdts < time.time() - total_secs)

    async with get_db_connection() as conn:
        result = await conn.execute(del_query)

    return result.rowcount


@celeryapp.task(bind=True, max_retries=1, default_retry_delay=10, autoretry_for=(Exception,))
def fetch_from_resources(self) -> None:
    logger.warning('Ready to start celery task: fetch_from_resources')  # todo: remove log
    async_to_sync(async_fetch_from_resources)()


@celeryapp.task()
def clear_expired_rows() -> None:
    logger.warning('Ready to clear expired rows in DB')
    rows_num = async_to_sync(async_clear_expired_rows)()
    logger.warning(f'Clear successful. {rows_num} rows cleared')
