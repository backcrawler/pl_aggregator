import dataclasses
from typing import Optional, List

from pydantic import BaseModel, Field


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
    page: int = Field(default_factory=lambda: 1, ge=1)


class PostInstance(BaseModel):
    title: str
    tags: Optional[str]
    ref: str
    site: str


class PostsResponse(BaseModel):
    posts: List[PostInstance]


class SitesAvailableResponse(BaseModel):
    sites: List[str]
