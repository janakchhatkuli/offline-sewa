"""Declarative SQLAlchemy base. Models import `Base` from here."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
