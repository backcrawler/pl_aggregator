import asyncio

import sqlalchemy

from ..database import get_table, get_db_connection
from ..loggers import logger
from ..resources.fetcher import work_on_resource


async def fetch_from_resources() -> None:
    logger.warning('Ready to start task: fetch_from_resources')
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
