from typing import List, Dict, Any, Callable, Awaitable

import httpx

FetchResults = List[Dict[str, Any]]

ParserFunc = Callable[[httpx.AsyncClient, str], Awaitable[FetchResults]]