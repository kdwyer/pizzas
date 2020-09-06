"""Unique topping names

Revision ID: 1b84b9e4be9c
Revises: d350d4c6305e
Create Date: 2020-11-26 17:47:33.826974

"""
import sqlalchemy as sa  # noqa: F401
from alembic import op  # noqa: F401

# revision identifiers, used by Alembic.
revision = "1b84b9e4be9c"
down_revision = "d350d4c6305e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f("uq_toppings_name"), "toppings", ["name"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("uq_toppings_name"), "toppings", type_="unique")
    # ### end Alembic commands ###