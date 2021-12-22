from typing import List, Callable, Awaitable

from .schemas import FetchResult

FetchResults = List[FetchResult]

ParserFunc = Callable[[str, int], Awaitable[FetchResults]]