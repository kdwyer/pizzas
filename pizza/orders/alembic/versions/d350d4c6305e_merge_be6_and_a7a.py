"""merge be6 and a7a

Revision ID: d350d4c6305e
Revises: be63a276c747, a7abb604ed89
Create Date: 2020-11-26 17:45:21.936281

"""
import sqlalchemy as sa  # noqa: F401
from alembic import op  # noqa: F401

# revision identifiers, used by Alembic.
revision = "d350d4c6305e"
down_revision = ("be63a276c747", "a7abb604ed89")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
