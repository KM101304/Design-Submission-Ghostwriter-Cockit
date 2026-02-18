from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    api_prefix: str = "/api/v1"
    openai_api_key: str = ""
    database_url: str = "sqlite+pysqlite:///:memory:"
    redis_url: str = "redis://localhost:6379/0"
    storage_backend: str = "local"
    storage_local_path: str = "./storage"
    storage_public_base_url: str = ""
    storage_bucket: str = "ghostwriter-artifacts"
    storage_s3_region: str = "us-east-1"
    storage_s3_endpoint: str = ""
    storage_s3_access_key: str = ""
    storage_s3_secret_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
