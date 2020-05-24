"""Models and database initialisation for the pizza package."""

import random
import string

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm


# TODO do we need to expose engine?
engine = None  # type: ignore
Session = None  # type: ignore


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = sa.MetaData(naming_convention=convention)


def init(url):
    """Initialise SQLAlchemy resources."""
    # FIXME global yuckiness
    global engine
    global Session
    engine = sa.create_engine(url)
    # FIXME manage sessions outside request handlers.
    Session = orm.scoped_session(orm.sessionmaker(bind=engine, expire_on_commit=False))
    return


# TODO - make base class with useful attributes.
Base = declarative_base(metadata=metadata)


class Pizza(Base):  # type: ignore
    """Database representation of a pizza."""

    __tablename__ = "pizzas"

    pizzas_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(64))
    price = sa.Column(sa.Integer)


class Order(Base):  # type: ignore
    """An order (header)."""

    __tablename__ = "orders"

    orders_id = sa.Column(sa.Integer, primary_key=True)
    reference = sa.Column(sa.String(6), unique=True)

    items = orm.relationship("Item")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference = "".join(
            [random.choice(string.ascii_letters) for _ in range(6)]
        )
        return


# One order has many items
# One item is one pizza


class Item(Base):  # type: ignore
    """A single order line-item."""

    __tablename__ = "items"

    items_id = sa.Column(sa.Integer, primary_key=True)
    orders_id = sa.Column(sa.Integer, sa.ForeignKey("orders.orders_id"))
    pizzas_id = sa.Column(sa.Integer, sa.ForeignKey("pizzas.pizzas_id"))

    pizza = orm.relationship("Pizza", backref=orm.backref("pizzas", uselist=False))
