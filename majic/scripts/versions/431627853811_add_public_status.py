"""
Add public status

Revision ID: 431627853811
Revises: 1d177c1e55aa
Create Date: 2015-04-28 15:07:43.307850

"""

# revision identifiers, used by Alembic.
from sqlalchemy.sql import table
from sqlalchemy import Column, String, SmallInteger
from joj.utils import constants

revision = '431627853811'
down_revision = '1d177c1e55aa'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

model_run_status = table('model_run_statuses',
        Column('id', SmallInteger, primary_key=True),
        Column('name', String(constants.DB_STRING_SIZE)))

def upgrade():
    """
    Add the data for PUBLIC runs
    :return: nothing
    """

    op.execute(
        model_run_status.insert({'name': constants.MODEL_RUN_STATUS_PUBLIC})
        )

def downgrade():
    """
    Downgrade the database
    :return: nothing
    """

    op.execute(
        model_run_status.delete().where(model_run_status.c.name == constants.MODEL_RUN_STATUS_PUBLIC)
        )
