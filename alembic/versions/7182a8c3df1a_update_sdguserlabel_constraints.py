"""Update SDGUserLabel constraints

Revision ID: 7182a8c3df1a
Revises: bdc1165d6ea0
Create Date: 2025-01-28 15:36:42.918286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = '7182a8c3df1a'
down_revision: Union[str, None] = 'bdc1165d6ea0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Check with: SHOW CREATE TABLE igcl.sdg_user_labels;
def upgrade():
    # Get a connection to the database
    conn = op.get_bind()

    # Drop the existing check constraints if they exist
    result = conn.execute(
        text("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_NAME = 'sdg_user_labels'
            AND CONSTRAINT_NAME = 'check_proposed_label_range'
        """)
    )
    if result.fetchone():
        op.drop_constraint('check_proposed_label_range', 'sdg_user_labels', type_='check')

    result = conn.execute(
        text("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_NAME = 'sdg_user_labels'
            AND CONSTRAINT_NAME = 'check_voted_label_range'
        """)
    )
    if result.fetchone():
        op.drop_constraint('check_voted_label_range', 'sdg_user_labels', type_='check')

    # Add the check constraints for proposed_label and voted_label
    op.create_check_constraint(
        'check_proposed_label_range',
        'sdg_user_labels',
        '(proposed_label >= 0 AND proposed_label <= 17)'
    )

    op.create_check_constraint(
        'check_voted_label_range',
        'sdg_user_labels',
        '(voted_label >= 0 AND voted_label <= 17)'
    )


def downgrade():
    # Drop the check constraints if they exist
    conn = op.get_bind()

    result = conn.execute(
        text("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_NAME = 'sdg_user_labels'
            AND CONSTRAINT_NAME = 'check_proposed_label_range'
        """)
    )
    if result.fetchone():
        op.drop_constraint('check_proposed_label_range', 'sdg_user_labels', type_='check')

    result = conn.execute(
        text("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_NAME = 'sdg_user_labels'
            AND CONSTRAINT_NAME = 'check_voted_label_range'
        """)
    )
    if result.fetchone():
        op.drop_constraint('check_voted_label_range', 'sdg_user_labels', type_='check')
