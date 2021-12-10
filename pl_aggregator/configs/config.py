from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str
    db_echo: bool
    db_name: str
    db_host: str
    db_port: str
    db_password: str
    db_user: str
    debug: bool
    host: str
    log_lvl: str
    port: int
    version: str

    class Config:
        env_file = './pl_aggregator/configs/.env'


@lru_cache()
def get_settings() -> Settings:
    return Settings()
