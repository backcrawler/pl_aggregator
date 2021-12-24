from functools import lru_cache
from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    allowed_hosts: List[str]
    app_name: str
    celery_broker_url: str
    celery_result_backend: str
    db_echo: bool
    db_name: str
    db_host: str
    db_port: str
    db_password: str
    db_user: str
    debug: bool
    fetch_wait_time: int
    host: str
    log_lvl: str
    minimum_reddit_score: int
    port: int
    post_days_ttl: int
    version: str

    class Config:
        env_file = './pl_aggregator/configs/.env'


@lru_cache()
def get_settings() -> Settings:
    return Settings()
