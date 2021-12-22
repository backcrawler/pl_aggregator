import importlib
import dataclasses

from sqlalchemy.dialects.postgresql import insert

from ..loggers import logger
from ..interfaces import FetchResults, ParserFunc
from ..exceptions import ResponceCodeError
from ..database import get_table, get_db_connection

m = importlib.import_module('pl_aggregator.resources.parsers')
parsers = {}
for key, val in vars(m).items():
    if key.endswith('_parser'):
        name = key[:-7]
        parsers[name] = val


async def work_on_resource(name: str, url: str, source_id: int) -> None:
    handler_func: ParserFunc = parsers[name]

    try:
        results: FetchResults = await handler_func(url, source_id)
    except ResponceCodeError as exc:
        logger.error(f'Got invalid response code: {exc.code} while fetching from resource: {name}')
    except Exception as exc:
        logger.exception(f'Exception: ( {exc} ) occurred while fetching from resource: {name}')
    else:
        post_t = get_table('post')
        logger.warning(f'RESULTS LEN: {len(results)}')
        async with get_db_connection() as conn:
            insert_query = insert(post_t).values([dataclasses.asdict(res) for res in results])
            await conn.execute(insert_query.on_conflict_do_nothing(index_elements=['ref']))
