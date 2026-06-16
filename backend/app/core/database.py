from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm import sessionmaker


import urllib.parse

# Safely encode the password to handle special characters like '@'
encoded_password = urllib.parse.quote_plus(settings.POSTGRES_PASSWORD)

DATABASE_URL = (
    f"postgresql://"
    f"{settings.POSTGRES_USER}:"
    f"{encoded_password}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)