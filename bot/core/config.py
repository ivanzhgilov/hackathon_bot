import pathlib
from typing import Literal
from urllib import parse

import pydantic.fields
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

base_project_dir_path = pathlib.Path(__file__).parent.parent.parent.resolve()

parse_settings = SettingsConfigDict(
    env_file=base_project_dir_path / '.env',
    env_file_encoding='utf-8',
    extra='ignore'
)


class DbConfig(BaseSettings):
    model_config = parse_settings

    db_host: str = Field()
    db_name: str = Field()
    db_port: int = Field()
    db_user: str = Field()
    db_password: str = Field()

    @pydantic.computed_field()
    def async_db_conn_str(self)->str:
        return f'postgresql+asyncpg://{self.db_user}:{parse.quote(self.db_password)}@{self.db_host}:{self.db_port}/{self.db_name}'


class Config(DbConfig):
    model_config = parse_settings

    bot_token: str = Field()
    log_level: Literal['DEBUG', 'INFO', 'ERROR', 'WARNING'] = Field('DEBUG')


config = Config()
