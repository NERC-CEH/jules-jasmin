"""
add workbench username to user

Revision ID: 8cf88e6f71d
Revises: 30b4cd1b3ebf
Create Date: 2015-04-08 14:32:01.562070

"""

# revision identifiers, used by Alembic.
revision = '8cf88e6f71d'
down_revision = '30b4cd1b3ebf'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    """
    Upgrade the database from nothing
    :return: nothing
    """
    op.add_column('users', sa.Column('workbench_username', sa.String(length=255), nullable=True))


def downgrade():
    """
    Downgrade the database
    :return: nothing
    """
    op.drop_column('users', 'workbench_username')
