from functools import lru_cache

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    database_url: str = Field(alias="DATABASE_URL")
    main_admin_ids_raw: str = Field(default="", alias="MAIN_ADMIN_IDS")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    page_size: int = Field(default=5, alias="PAGE_SIZE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @computed_field
    @property
    def main_admin_ids(self) -> set[int]:
        values: set[int] = set()
        for raw_id in self.main_admin_ids_raw.split(","):
            raw_id = raw_id.strip()
            if raw_id:
                values.add(int(raw_id))
        return values


@lru_cache
def get_settings() -> Settings:
    return Settings()
