from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://admin:qwerty@localhost:5432/wallets"

    class Config:
        env_file = ".env"


settings = Settings()