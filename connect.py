import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import metadata


def get_engine():
    engine = create_engine(os.getenv('DATABASE_URL'), echo=True)
    return engine


def connect():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def create_db():
    engine = get_engine()
    metadata.create_all(engine)


create_db()
