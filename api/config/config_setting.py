from pydantic_settings import BaseSettings, SettingsConfigDict


class config_setting(BaseSettings):
    DATABASE_URL: str
    DIRECT_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = config_setting()
