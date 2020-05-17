"""Models and database initialisation for the pizza package."""

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm


# TODO do we need to expose engine?
engine = None  # type: ignore
Session = None  # type: ignore


def init(url):
    """Initialise SQLAlchemy resources."""
    # FIXME global yuckiness
    global engine
    global Session
    engine = sa.create_engine(url)
    Session = orm.scoped_session(orm.sessionmaker(bind=engine))
    return


# TODO - make base class with useful attributes.
Base = declarative_base()


class Pizza(Base):  # type: ignore
    """Database representation of a pizza."""

    __tablename__ = "pizzas"

    pizzas_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(64))
    price = sa.Column(sa.Integer)
