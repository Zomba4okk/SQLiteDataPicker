from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from settings import settings


engine = create_engine(
    settings.DB_URI,
    echo=settings.DB_ECHO
)

Session = sessionmaker(engine)
