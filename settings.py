import os

from pydantic import BaseSettings

__all__ = ("settings",)


default_db_file_path = os.path.join(os.getcwd(), "Chinook_Sqlite.sqlite")


class Settings(BaseSettings):
    ENV: str = "local"
    DB_DRIVER: str = "sqlite+pysqlite:///"
    DB_ECHO: bool = False
    DB_URL: str = default_db_file_path

    @property
    def DB_URI(self):
        return f"{self.DB_DRIVER}{self.DB_URL}"


settings = Settings(
    _env_file=os.path.join(os.getcwd(), f".{os.getenv('ENV', 'local')}.env"),
    _env_file_encoding="utf-8"
)
