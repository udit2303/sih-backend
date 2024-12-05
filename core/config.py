from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    debug: bool = False
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
