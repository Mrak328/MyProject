from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:12345@localhost:5432/aviko"

    class Config:
        env_file = ".env"


settings = Settings()