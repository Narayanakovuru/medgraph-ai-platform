from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str = "MedGraph AI"
    APP_VERSION: str = "1.0.0"

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    class Config:
        env_file = ".env"


settings = Settings()
