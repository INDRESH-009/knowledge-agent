from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AI Document Intelligence Agent"
    APP_ENV: str = "local"

    DATABASE_URL: str
    LOCAL_STORAGE_DIR: str = "storage/uploads"

    class Config:
        env_file = ".env"


settings = Settings()