"""Unique pizza names

Revision ID: be63a276c747
Revises: c3f87ade5aee
Create Date: 2020-11-26 13:09:53.461140

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "be63a276c747"
down_revision = "c3f87ade5aee"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f("uq_pizzas_name"), "pizzas", ["name"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f("uq_pizzas_name"), "pizzas", type_="unique")
    # ### end Alembic commands ###
