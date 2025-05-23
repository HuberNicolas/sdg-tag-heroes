"""Update ScenarioType enum to include DECIDED

Revision ID: 8e1be5e54d96
Revises: 602781c4750e
Create Date: 2025-02-10 14:09:10.299662

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum

# revision identifiers, used by Alembic.
revision: str = '8e1be5e54d96'
down_revision: Union[str, None] = '602781c4750e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update the 'scenariotype' enum to include 'DECIDED'
    op.alter_column(
        'sdg_label_decisions',
        'scenario_type',
        type_=Enum('CONFIRM', 'TIEBREAKER', 'INVESTIGATE', 'EXPLORE', 'NOT_ENOUGH_VOTES',
                   'NO_SPECIFIC_SCENARIO', 'DECIDED', name='scenariotype'),
        existing_type=sa.Enum('CONFIRM', 'TIEBREAKER', 'INVESTIGATE', 'EXPLORE',
                              'NOT_ENOUGH_VOTES', 'NO_SPECIFIC_SCENARIO', name='scenariotype'),
        nullable=False
    )


def downgrade() -> None:
    # Revert the 'scenariotype' enum to its original state without 'DECIDED'
    op.alter_column(
        'sdg_label_decisions',
        'scenario_type',
        type_=Enum('CONFIRM', 'TIEBREAKER', 'INVESTIGATE', 'EXPLORE', 'NOT_ENOUGH_VOTES',
                   'NO_SPECIFIC_SCENARIO', name='scenariotype'),
        existing_type=sa.Enum('CONFIRM', 'TIEBREAKER', 'INVESTIGATE', 'EXPLORE',
                              'NOT_ENOUGH_VOTES', 'NO_SPECIFIC_SCENARIO', name='scenariotype'),
        nullable=False
    )
