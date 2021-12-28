import dataclasses
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


@dataclasses.dataclass
class FetchResult:
    title: str
    ref: str
    tags: Optional[str]
    sourceid: int
    createdts: int


class PostsParams(BaseModel):
    sites: List[str]
    langs: List[str]


class PostInstance(BaseModel):
    title: str
    tags: Optional[str]
    ref: str
    site: str


class PostsResponse(BaseModel):
    posts: List[PostInstance]


class SitesAvailableResponse(BaseModel):
    sites: List[str]
