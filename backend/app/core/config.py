from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    api_prefix: str = "/api/v1"
    openai_api_key: str = ""
    database_url: str = "postgresql+psycopg://postgres:postgres@db:5432/ghostwriter"
    redis_url: str = "redis://localhost:6379/0"
    auth_disabled: bool = False
    auth_secret_key: str = "change-me-now"
    auth_access_token_exp_minutes: int = 120
    auth_password_salt: str = "ghostwriter-salt"
    auth_seed_tenant_id: str = "demo-brokerage"
    auth_seed_email: str = "admin@ghostwriter.dev"
    auth_seed_password: str = "ChangeMe123!"
    sentry_dsn: str = ""
    log_level: str = "INFO"
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
