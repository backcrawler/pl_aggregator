import asyncio
import time

import sqlalchemy
from asgiref.sync import async_to_sync
import celery
from celery.result import AsyncResult
from celery import chain

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


@celeryapp.task(bind=True)
def start_chain(self):
    logger.warning('Chain started')
    time.sleep(1)


@celeryapp.task(bind=True)
def add(self, x: int, y: int):
    result = x + y
    logger.warning(f'add ready: {result}')
    time.sleep(2)
    logger.warning(f'add competed: {result}')
    return result


@celeryapp.task(bind=True)
def exc(self, arg):
    logger.warning('exc ready')
    time.sleep(1)
    raise Exception(f'Y R FUCKED WITH ARG: {arg}')


@celeryapp.task(bind=True)
def mul(self, x: int, y: int):
    logger.warning('mul ready')
    time.sleep(1)
    return x * y


@celeryapp.task(bind=True)
def end_chain(self, res):
    logger.warning('end ready')
    time.sleep(1)
    logger.warning(f'Chain ended. RES: {res}')


@celeryapp.task(bind=True)
def log_err(self, name, *args, **kwargs):
    logger.error(f'ERRORS HERE FOR {name}. ARGS: {args}; KW: {kwargs}')


@celeryapp.task
def on_error_handler(context, *args, excluded_id=None, result_ids=None, **kwargs):
    logger.warning(f'ON ERROR FOR {excluded_id}; KW: {kwargs}; IDS: {result_ids}')
    logger.warning(f'{context.kwargs}')
    logger.warning(f'{dir(context)}')
    for async_res_list in result_ids:
        for async_res_id in async_res_list:
            if async_res_id == excluded_id:
                logger.warning(f'Skipping shit {excluded_id}')
                continue
            celeryapp.control.revoke(async_res_id, terminate=True)
            logger.warning(f'RES {async_res_id} JUST REVOKED')


def mypartial(func, *args, **kwargs):
    def inner(*nargs, **nkwargs):
        mod_args = list(args) + list(nargs)
        mod_kwargs = {**kwargs, **nkwargs}
        return func(*mod_args, **mod_kwargs)
    return inner


class MyTask(celery.Task):

    def __init__(self, *args, ids=None, **kwargs):
        self.ids = ids
        super().__init__(*args, **kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print('{0!r} failed: {1!r}'.format(task_id, exc))


@celeryapp.task
def my_on_error_handler(context, *args, **kwargs):
    parent = AsyncResult(context.parent_id, app=celeryapp)
    for child in parent.children[0].children:
        child.revoke(terminate=True)
        logger.warning(f'{child} REVOKED')
    # celeryapp.control.revoke(context.parent_id, terminate=True)


@celeryapp.task
def my_group():
    chain_results_ids = []
    collections = [(add, [1, 0]), (exc, [0]), (add, [2, 0])]
    logger.warning(f'GOT COLLECTIONS: {collections}')
    # gr = celery.group(*[task.si(*args).on_error(my_on_error_handler.s()) for task, args in collections])
    gr = celery.group(*[task.si(*args) for task, args in collections]).on_error(my_on_error_handler.s())
    results = gr.delay()
    to_return = []
    for child in results.children:
        to_return.append(child.as_list())
    return to_return


@celeryapp.task
def start_as_group():
    def _on_error_handler(excluded_id=None, result_ids=None):
        logger.warning(f'ON ERROR FOR {excluded_id}; IDS: {result_ids}')
        for async_res_list in result_ids:
            for async_res_id in async_res_list:
                if async_res_id == excluded_id:
                    logger.warning(f'Skipping shit {excluded_id}')
                    continue
                celeryapp.control.revoke(async_res_id, terminate=True)
                logger.warning(f'RES {async_res_id} JUST REVOKED')

    chain_results_ids = []
    collections = [(add, [1,0]), (exc, [0]), (add, [2,0])]
    logger.warning(f'GOT COLLECTIONS: {collections}')
    for i, (task, args) in enumerate(collections):
        created = task.si(*args)
        created.on_error(on_error_handler.s(result_ids=chain_results_ids, excluded_id=i))
        # created.on_error(mypartial(_on_error_handler, excluded_id=i, result_ids=chain_results_ids))
        chain_result = created.delay()
        list_result = chain_result.as_list()
        chain_results_ids.append(list_result)
        logger.warning(f'CHAIN IDS: {chain_results_ids}')
        logger.warning(f'RESULT: {list_result} {type(list_result[0])} FOR {sum(args)}')

    return chain_results_ids


@celeryapp.task(bind=True)
def wait_for_group(self, chain_results_ids):
    logger.warning(f'WAIT GOT RESULTS: {chain_results_ids}')
    return chain_results_ids


@celeryapp.task(bind=True)
def work_for_group(self, chain_results_ids):
    logger.warning(f'WORK GOT RESULTS: {chain_results_ids}')
    return chain_results_ids