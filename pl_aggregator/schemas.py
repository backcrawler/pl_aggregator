import dataclasses
from typing import Optional


@dataclasses.dataclass
class FetchResult:
    title: str
    ref: str
    tags: Optional[str]
    sourceid: int
    createdts: int
