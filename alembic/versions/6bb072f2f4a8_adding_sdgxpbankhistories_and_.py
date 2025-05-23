"""Adding SDGXPBankHistories and SDGCoinWalletHistories

Revision ID: 6bb072f2f4a8
Revises: 58a824784685
Create Date: 2024-12-09 15:17:36.874250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bb072f2f4a8'
down_revision: Union[str, None] = '58a824784685'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sdg_coin_wallet_histories',
    sa.Column('history_id', sa.Integer(), nullable=False),
    sa.Column('wallet_id', sa.Integer(), nullable=False),
    sa.Column('increment', sa.Float(), nullable=False),
    sa.Column('reason', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['wallet_id'], ['sdg_coin_wallets.sdg_coin_wallet_id'], ),
    sa.PrimaryKeyConstraint('history_id')
    )
    op.create_index(op.f('ix_sdg_coin_wallet_histories_history_id'), 'sdg_coin_wallet_histories', ['history_id'], unique=False)
    op.create_table('sdg_xp_bank_histories',
    sa.Column('history_id', sa.Integer(), nullable=False),
    sa.Column('xp_bank_id', sa.Integer(), nullable=False),
    sa.Column('increment', sa.Float(), nullable=False),
    sa.Column('reason', sa.String(length=255), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['xp_bank_id'], ['sdg_xp_banks.sdg_xp_bank_id'], ),
    sa.PrimaryKeyConstraint('history_id')
    )
    op.create_index(op.f('ix_sdg_xp_bank_histories_history_id'), 'sdg_xp_bank_histories', ['history_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_sdg_xp_bank_histories_history_id'), table_name='sdg_xp_bank_histories')
    op.drop_table('sdg_xp_bank_histories')
    op.drop_index(op.f('ix_sdg_coin_wallet_histories_history_id'), table_name='sdg_coin_wallet_histories')
    op.drop_table('sdg_coin_wallet_histories')
    # ### end Alembic commands ###
