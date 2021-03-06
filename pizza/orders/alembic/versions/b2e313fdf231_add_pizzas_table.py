"""Add pizzas table

Revision ID: b2e313fdf231
Revises:
Create Date: 2020-05-17 19:24:16.467788

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2e313fdf231"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pizzas",
        sa.Column("pizzas_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=True),
        sa.Column("price", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("pizzas_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("pizzas")
    # ### end Alembic commands ###
