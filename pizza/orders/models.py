"""Models and database initialisation for the pizza package."""

import functools
import random
import string
import sys
from typing import List

import bottle
import sqlalchemy as sa
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
    engine = sa.create_engine(url, echo=True)
    Session = orm.scoped_session(
        orm.sessionmaker(bind=engine), scopefunc=lambda: bottle.request
    )
    return


# TODO - make base class with useful attributes.
Base = orm.declarative_base(metadata=metadata)


class Pizza(Base):  # type: ignore
    """Database representation of a pizza."""

    __tablename__ = "pizzas"

    pizzas_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(64), unique=True)
    price = sa.Column(sa.Integer)

    def __repr__(self):
        return f"Pizza(name='{self.name}')"


class Topping(Base):  # type: ignore
    """Database representation of pizza toppings."""

    __tablename__ = "toppings"

    toppings_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(64), unique=True)
    price = sa.Column(sa.Integer)

    def __repr__(self) -> str:
        return f"Topping(name='{self.name}')"


class Item(Base):  # type: ignore
    """A single order line-item."""

    __tablename__ = "items"

    items_id = sa.Column(sa.Integer, primary_key=True)
    orders_id = sa.Column(sa.Integer, sa.ForeignKey("orders.orders_id"))
    pizzas_id = sa.Column(sa.Integer, sa.ForeignKey("pizzas.pizzas_id"))
    toppings_id = sa.Column(sa.Integer, sa.ForeignKey("toppings.toppings_id"))

    pizza = orm.relationship("Pizza", backref=orm.backref("pizzas", uselist=False))
    topping = orm.relationship("Topping", backref=orm.backref("toppings"))

    @property
    def name(self) -> str:
        """Compute the name of this item."""
        return self.topping.name if self.topping else self.pizza.name

    @property
    def price(self) -> int:
        """Compute the price of this item."""
        return self.topping.price if self.topping else self.pizza.price

    def __repr__(self) -> str:
        pn = self.pizza.name if self.pizza else ""
        tn = self.topping.name if self.topping else ""
        return f"Item(pizza='{pn}', topping='{tn}')"


class Order(Base):  # type: ignore
    """An order (header)."""

    __tablename__ = "orders"

    orders_id = sa.Column(sa.Integer, primary_key=True)
    reference = sa.Column(sa.String(6), unique=True)

    items = orm.relationship("Item", uselist=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reference = "".join(
            [random.choice(string.ascii_letters) for _ in range(6)]
        )
        return

    def by_item(self) -> List[Item]:
        """Fetch ordered by pizza name then item name."""
        # FIXME: orders with more than one pizza of a type.
        session = Session.object_session(self)  # type: ignore
        # The outer join on Topping ensures that we get all the items.
        # If we use a normal join we don't get the Pizza items, because
        # those items' toppins_id is NULL.
        items = (
            session.query(Item)
            .join(Pizza)
            .outerjoin(Topping)
            .filter(Item.orders_id == self.orders_id)
            .order_by(Pizza.name, sa.func.coalesce(Topping.name, ""))
        )
        return items

    @property
    def total(self) -> int:
        """Compute the total price of the order."""
        return sum(i.price for i in self.items)


def manage_session(func):
    """
    Decorator that manages a scoped session's lifecycle.

    Using a decorator permits accessing model instance attributes inside
    templates without having to set `expire=False` on the session.

    This decorator needs to be placed *after* the route decorator
    (I think because the request ends at route exit, and then the session
    gets removed).

    TODO: consider bottle-sqlalchemy plugin.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            rval = func(*args, **kwargs)
            session.commit()
            return rval
        except:  # noqa: E722
            # Bottle handles redirects by raising the response as an
            # exception, so in this case we need to commit
            # rather than roll back.
            if isinstance(sys.exc_info()[1], bottle.HTTPResponse):
                session.commit()
                raise
            session.rollback()
            raise

    return wrapper


def remove_session() -> None:
    """Remove a scoped session."""
    # TODO do we need this indirection?
    Session.remove()  # type: ignore
