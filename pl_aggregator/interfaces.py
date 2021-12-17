from typing import List, Dict, Any, Callable, Awaitable

from .schemas import FetchResult

FetchResults = List[Dict[str, Any]]

ParserFunc = Callable[[str, int], Awaitable[FetchResults]]