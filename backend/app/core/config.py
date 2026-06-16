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

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    QDRANT_URL: str
    QDRANT_API_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
