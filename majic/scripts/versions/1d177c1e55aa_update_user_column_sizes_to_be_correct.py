"""
update user column sizes to be correct

Revision ID: 1d177c1e55aa
Revises: 8cf88e6f71d
Create Date: 2015-04-10 13:10:12.900778

"""

# revision identifiers, used by Alembic.
from joj.utils import constants

revision = '1d177c1e55aa'
down_revision = '8cf88e6f71d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Upgrade the database from nothing
    :return: nothing
    """

    op.alter_column("users", "username", type_=sa.String(constants.DB_LONG_STRING_SIZE))
    op.alter_column("users", "name", type_=sa.String(2 * constants.DB_STRING_SIZE))


def downgrade():
    """
    Downgrade the database
    :return: nothing
    """
    op.alter_column("users", "username", type_=sa.String(constants.DB_STRING_SIZE))
    op.alter_column("users", "name", type_=sa.String(constants.DB_STRING_SIZE))
