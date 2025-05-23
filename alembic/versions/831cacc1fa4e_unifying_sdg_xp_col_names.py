"""Unifying SDG_XP col names

Revision ID: 831cacc1fa4e
Revises: 44f2663a68ed
Create Date: 2025-01-21 12:59:01.112183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '831cacc1fa4e'
down_revision: Union[str, None] = '44f2663a68ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sdg_xp_banks', sa.Column('sdg1_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg2_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg3_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg4_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg5_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg6_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg7_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg8_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg9_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg10_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg11_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg12_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg13_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg14_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg15_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg16_xp', sa.Float(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg17_xp', sa.Float(), nullable=False))
    op.drop_column('sdg_xp_banks', 'sdg_11_xp')
    op.drop_column('sdg_xp_banks', 'sdg_13_xp')
    op.drop_column('sdg_xp_banks', 'sdg_8_xp')
    op.drop_column('sdg_xp_banks', 'sdg_17_xp')
    op.drop_column('sdg_xp_banks', 'sdg_15_xp')
    op.drop_column('sdg_xp_banks', 'sdg_4_xp')
    op.drop_column('sdg_xp_banks', 'sdg_5_xp')
    op.drop_column('sdg_xp_banks', 'sdg_1_xp')
    op.drop_column('sdg_xp_banks', 'sdg_9_xp')
    op.drop_column('sdg_xp_banks', 'sdg_3_xp')
    op.drop_column('sdg_xp_banks', 'sdg_10_xp')
    op.drop_column('sdg_xp_banks', 'sdg_7_xp')
    op.drop_column('sdg_xp_banks', 'sdg_12_xp')
    op.drop_column('sdg_xp_banks', 'sdg_14_xp')
    op.drop_column('sdg_xp_banks', 'sdg_16_xp')
    op.drop_column('sdg_xp_banks', 'sdg_6_xp')
    op.drop_column('sdg_xp_banks', 'sdg_2_xp')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sdg_xp_banks', sa.Column('sdg_2_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_6_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_16_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_14_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_12_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_7_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_10_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_3_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_9_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_1_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_5_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_4_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_15_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_17_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_8_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_13_xp', mysql.FLOAT(), nullable=False))
    op.add_column('sdg_xp_banks', sa.Column('sdg_11_xp', mysql.FLOAT(), nullable=False))
    op.drop_column('sdg_xp_banks', 'sdg17_xp')
    op.drop_column('sdg_xp_banks', 'sdg16_xp')
    op.drop_column('sdg_xp_banks', 'sdg15_xp')
    op.drop_column('sdg_xp_banks', 'sdg14_xp')
    op.drop_column('sdg_xp_banks', 'sdg13_xp')
    op.drop_column('sdg_xp_banks', 'sdg12_xp')
    op.drop_column('sdg_xp_banks', 'sdg11_xp')
    op.drop_column('sdg_xp_banks', 'sdg10_xp')
    op.drop_column('sdg_xp_banks', 'sdg9_xp')
    op.drop_column('sdg_xp_banks', 'sdg8_xp')
    op.drop_column('sdg_xp_banks', 'sdg7_xp')
    op.drop_column('sdg_xp_banks', 'sdg6_xp')
    op.drop_column('sdg_xp_banks', 'sdg5_xp')
    op.drop_column('sdg_xp_banks', 'sdg4_xp')
    op.drop_column('sdg_xp_banks', 'sdg3_xp')
    op.drop_column('sdg_xp_banks', 'sdg2_xp')
    op.drop_column('sdg_xp_banks', 'sdg1_xp')
    # ### end Alembic commands ###
