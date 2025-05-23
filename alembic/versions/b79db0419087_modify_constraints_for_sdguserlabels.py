"""Modify constraints for SDGUserLabels

Revision ID: b79db0419087
Revises: 166401996811
Create Date: 2025-01-28 15:52:10.865185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'b79db0419087'
down_revision: Union[str, None] = '166401996811'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
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

    # Add the new check constraints for proposed_label and voted_label with the updated range (-1 to 18)
    op.create_check_constraint(
        'check_proposed_label_range',
        'sdg_user_labels',
        '(proposed_label >= -1 AND proposed_label <= 18)'
    )

    op.create_check_constraint(
        'check_voted_label_range',
        'sdg_user_labels',
        '(voted_label >= -1 AND voted_label <= 18)'
    )



def downgrade() -> None:
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

    # Add the old check constraints for proposed_label and voted_label with the original range (0 to 17)
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
