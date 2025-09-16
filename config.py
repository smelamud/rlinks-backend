from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    http_host: str = "0.0.0.0"
    http_port: int = 8000

    db_host: str = "localhost"
    db_port: int = 5455
    db_name: str = "rlinks"
    db_user: str = "rlinks"
    db_password: str = "rlinks"
    graph_name: str = "rlinks"

    model_config = SettingsConfigDict(
        env_file=".env",                # load .env if present
        env_file_encoding="utf-8",      # but real env vars still win
        extra="ignore",
    )


config = Config()
