import importlib

from ..loggers import logger
from ..interfaces import FetchResults, ParserFunc
from ..exceptions import ResponceCodeError

m = importlib.import_module('pl_aggregator.resources.parsers')
parsers = {}
for key, val in vars(m).items():
    if key.endswith('_parser'):
        name = key[:-7]
        parsers[name] = val


async def work_on_resource(httpx_client, name: str, url: str):
    handler_func: ParserFunc = parsers[name]

    try:
        results: FetchResults = await handler_func(httpx_client, url)
    except ResponceCodeError as exc:
        logger.error(f'Got invalid response code: {exc.code} while fetching from resource: {name}')
    except Exception as exc:
        logger.exception(f'Exception: ( {exc} ) occurred while fetching from resource: {name}')
    else:
        for res in results:
            ...
