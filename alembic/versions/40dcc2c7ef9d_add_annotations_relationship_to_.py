"""Add annotations relationship to SDGLabelDecision

Revision ID: 40dcc2c7ef9d
Revises: 733326aabde3
Create Date: 2025-01-20 10:03:53.340868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40dcc2c7ef9d'
down_revision: Union[str, None] = '733326aabde3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
