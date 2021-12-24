from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse

from .database import get_db_connection
from .celerytasks import fetch_from_resources

router = APIRouter()


@router.get('/', response_class=HTMLResponse)  # todo: change for nginx
async def root():
    return HTMLResponse(content=..., status_code=200)


@router.get('/test-conn')
async def test():
    fetch_from_resources.delay()

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.get('/test-task')
async def test():
    from .celerytasks.tasks import async_fetch_from_resources
    await async_fetch_from_resources()

    return JSONResponse(content={'result': 'ok'}, status_code=200)
