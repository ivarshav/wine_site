from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app.env_variables import URI
from src.app.models import metadata


def get_engine():
    engine = create_engine(URI, echo=True)
    return engine


def connect():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_db():
    engine = get_engine()
    metadata.create_all(engine)


create_db()
