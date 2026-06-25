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
    QDRANT_MODE: str
    QDRANT_HOST: str | None = None
    QDRANT_PORT: int | None = None
    QDRANT_COLLECTION_NAME: str
    QDRANT_VECTOR_SIZE: int
    QDRANT_DISTANCE: str

    EMBEDDING_MODEL_NAME: str = "dmis-lab/biobert-base-cased-v1.1"
    EMBEDDING_DEVICE: str = "auto"
    EMBEDDING_MAX_LENGTH: int = 512

    class Config:
        env_file = ".env"


settings = Settings()
