import pathlib
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

base_project_dir_path = pathlib.Path(__file__).parent.parent.parent.resolve()

parse_settings = SettingsConfigDict(
    env_file=base_project_dir_path / '.env',
    env_file_encoding='utf-8',
)


class DbConfig(BaseSettings):
    model_config = parse_settings

    db_name: str = Field()
    db_port: int = Field()
    db_user: str = Field()
    db_password: str = Field()


class Config(DbConfig):
    model_config = parse_settings

    bot_token: str = Field()
    log_level: Literal['DEBUG', 'INFO', 'ERROR', 'WARNING'] = Field('DEBUG')


config = Config()
