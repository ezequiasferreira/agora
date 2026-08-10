from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "agora"
    db_user: str = "postgres"
    db_password: str = ""
    query_timeout_ms: int = 3000
    max_rows: int = 1000
    pool_max: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()