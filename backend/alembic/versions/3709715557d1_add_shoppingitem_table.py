"""add shoppingitem table

Revision ID: 3709715557d1
Revises: 4a1f1b246cb2
Create Date: 2026-08-16 10:36:12.958876

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3709715557d1'
down_revision: Union[str, Sequence[str], None] = '4a1f1b246cb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'shoppingitem',
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('quantity', sa.String(), nullable=True),
        sa.Column('done', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('shoppingitem')
