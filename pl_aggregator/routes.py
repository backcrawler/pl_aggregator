from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from celery import group, chord, chain

from .database import get_db_connection
from .loggers import logger
from .celerytasks import fetch_from_resources, start_chain, add, mul, end_chain, exc, log_err, start_as_group, my_group

router = APIRouter()


@router.get('/', response_class=HTMLResponse)  # todo: change for nginx
async def root():
    return HTMLResponse(content=..., status_code=200)


@router.get('/test-conn')
async def test():
    chain = start_chain.s() | add.si(10, 20) | mul.s(5) | end_chain.s()
    chain.on_error(log_err.si('hui'))
    res = chain.delay()
    res2 = mul.apply_async(args=[10,5])
    logger.warning(f'MUL RES: {res2}; MUL TYPE: {type(res2)}')
    logger.warning(f'RESES: {res.as_list()}')

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.get('/test-conn-2')
async def test():
    gr = chord([add.si(1,1), add.si(2,2), add.si(3,3), exc.si('hui')])
    callback = end_chain.s().set(link_error=log_err.s())
    gr(callback)

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.get('/test-conn-3')
async def test():
    res = chord((add.s(i, i) for i in range(10)), end_chain.s())()
    res.get()

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.get('/test-conn-4')
async def test():
    # collections = [(add, [1,0]), (exc, [0]), (add, [2,0])]
    collections = [add.si(1,0), exc.si(0), add.si(2,0)]
    group = my_group.si()
    group.delay()

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.get('/test-task')
async def test():
    from .celerytasks.tasks import async_fetch_from_resources
    await async_fetch_from_resources()

    return JSONResponse(content={'result': 'ok'}, status_code=200)
