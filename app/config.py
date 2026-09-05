from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    api_key_lms: str
    events_provider_url: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
