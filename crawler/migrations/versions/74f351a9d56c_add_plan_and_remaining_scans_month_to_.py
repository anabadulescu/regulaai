"""Add plan and remaining_scans_month to Organisation

Revision ID: 74f351a9d56c
Revises: 3c09800c3657
Create Date: 2025-06-18 16:15:50.824397

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74f351a9d56c'
down_revision: Union[str, None] = '3c09800c3657'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organisations', sa.Column('plan', sa.String(length=50), nullable=False))
    op.add_column('organisations', sa.Column('remaining_scans_month', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('organisations', 'remaining_scans_month')
    op.drop_column('organisations', 'plan')
    # ### end Alembic commands ###
