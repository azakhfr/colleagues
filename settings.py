import pathlib

from pydantic import BaseSettings


class DataBaseSettings(BaseSettings):
    user: str = "sbis"
    password: str = "sbis"
    host: str = "127.0.0.1"
    port: str = "5433"

    class Config:
        env_prefix = "DATABASE_"


ROOT = pathlib.Path(__file__).parent.absolute()
data_base_settings = DataBaseSettings()
