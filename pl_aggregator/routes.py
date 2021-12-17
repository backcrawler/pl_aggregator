from fastapi import APIRouter
from fastapi.responses import JSONResponse, HTMLResponse

from .database import get_db_connection

router = APIRouter()


@router.get('/', response_class=HTMLResponse)  # todo: change for nginx
async def root():
    return HTMLResponse(content=..., status_code=200)


@router.get('/test-conn')
async def test():
    from sqlalchemy.sql import text
    insert = text(f'''INSERT INTO test(id, username, age) VALUES (2, 'Mike', 10)''')
    sql_select = text('SELECT * FROM test')
    async with get_db_connection() as conn:
        await conn.execute(insert)
        res = await conn.execute(sql_select)
        rows = res.fetchall()
        print(rows)

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.get('/test-task')
async def test():
    from .celerytasks.tasks import fetch_from_resources
    await fetch_from_resources()

    return JSONResponse(content={'result': 'ok'}, status_code=200)
