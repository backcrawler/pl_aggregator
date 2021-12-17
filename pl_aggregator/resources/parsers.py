import json
import time
from urllib.parse import urlparse, urlunparse, urljoin

import httpx
from bs4 import BeautifulSoup

from ..interfaces import FetchResults
from ..configs import get_settings
from ..exceptions import ResponceCodeError

heading = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
possible_tags = {'python', 'c#', 'javascript', 'c++', 'java', 'php', 'kotlin', 'haskell', 'big data'}
settings = get_settings()


async def get_soup(url: str) -> BeautifulSoup:
    '''Basic function for bs4-like sources'''
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=heading, timeout=settings.fetch_wait_time)
    if r.status_code != 200:
        raise ResponceCodeError(r.status_code)
    content = r.content
    soup = BeautifulSoup(content, "html.parser")
    return soup


def get_base(link: str) -> str:
    parsed = urlparse(link)
    base = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
    return base


async def habr_parser(url: str, source_id: int) -> FetchResults:
    soup = await get_soup(url)
    articles = soup.findAll('article', class_="post_preview")
    posts = []

    for article in articles:
        ref = article.find('a', class_="post__title_link")
        base = get_base(url)
        instance = {'title': ref.text, 'ref': urljoin(base, ref['href']), 'tags': None}
        posts.append(instance)

    return posts


async def reddit_base(url: str, source_id: int) -> FetchResults:
    async with httpx.AsyncClient() as client:
        r = await client.get(urljoin(url, '.json'), headers=heading, timeout=settings.fetch_wait_time)
    if r.status_code != 200:
        raise ResponceCodeError(r.status_code)

    json_obj = json.loads(r.content)
    children = json_obj['data']['children']
    base = get_base(url)
    posts = []

    for i in range(len(children)):
        if children[i]['data']['score'] < settings.minimum_reddit_score:
            continue
        instance = {
            'title': children[i]['data']['title'],
            'ref': urljoin(base, children[i]['data']['permalink']),
            'tags': None,
            'sourceid': source_id,
            'createdts': int(time.time())
        }
        posts.append(instance)

    if len(posts) > 20:
        posts = posts[:20]

    return posts


async def reddit_programming_parser(url: str, source_id: int) -> FetchResults:
    return await reddit_base(url, source_id)
