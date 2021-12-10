import uvicorn

from pl_aggregator.server import app
from pl_aggregator.configs import get_settings


if __name__ == '__main__':
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
