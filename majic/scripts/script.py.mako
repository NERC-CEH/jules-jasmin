"""
${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

def upgrade():
    """
    Upgrade the database from nothing
    :return: nothing
    """

    ${upgrades if upgrades else "pass"}


def downgrade():
    """
    Downgrade the database
    :return: nothing
    """
    ${downgrades if downgrades else "pass"}
