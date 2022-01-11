from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, and_

from .database import get_db_connection, get_table
from .celerytasks import clear_expired_rows
from .loggers import logger
from .configs import get_settings
from .schemas import PostsParams, PostsResponse, PostInstance, SitesAvailableResponse

router = APIRouter()


@router.get('/', response_class=HTMLResponse)  # todo: change for nginx
async def root():
    return HTMLResponse(content=..., status_code=200)


@router.get('/test-conn')
async def test():
    clear_expired_rows.delay()

    return JSONResponse(content={'result': 'ok'}, status_code=200)


@router.post('/posts')
async def receive_posts(post_params: PostsParams):
    post_t = get_table('post')
    source_t = get_table('source')
    site_t = get_table('site')
    settings = get_settings()

    select_query = select(post_t.c.title, post_t.c.tags, post_t.c.ref, site_t.c.name).select_from(
        post_t.join(source_t, onclause=post_t.c.sourceid == source_t.c.id).join(
            site_t, onclause=source_t.c.siteid == site_t.c.id)
        ).where(
            and_(
                site_t.c.active == True,
                site_t.c.lang.in_(post_params.langs),
                site_t.c.name.in_(post_params.sites),
            )
        ).order_by(
            post_t.c.createdts
        ).limit(
            settings.page_len
        ).offset(
            (post_params.page - 1) * settings.page_len
        )

    async with get_db_connection() as conn:
        posts_cursor = await conn.execute(select_query)
        post_rows = posts_cursor.fetchall()

    posts_to_send = [PostInstance(title=row.title, tags=row.tags, ref=row.ref, site=row.name) for row in post_rows]
    encoded = jsonable_encoder(posts_to_send)

    return JSONResponse(content=encoded, status_code=200)


@router.get('/sites-available', response_model=SitesAvailableResponse)
async def get_sites_available():
    site_t = get_table('site')
    select_query = select(site_t.c.name).where(site_t.c.active==True)
    async with get_db_connection() as conn:
        site_names = await conn.execute(select_query)

    return SitesAvailableResponse(sites=[site.name for site in site_names])
