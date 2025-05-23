"""Add entropy and std for sdg_predictions

Revision ID: 33010b178e40
Revises: b79db0419087
Create Date: 2025-01-29 14:57:04.319444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33010b178e40'
down_revision: Union[str, None] = 'b79db0419087'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sdg_predictions', sa.Column('entropy', sa.Float(precision=4), nullable=False))
    op.add_column('sdg_predictions', sa.Column('std', sa.Float(precision=4), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sdg_predictions', 'std')
    op.drop_column('sdg_predictions', 'entropy')
    # ### end Alembic commands ###
