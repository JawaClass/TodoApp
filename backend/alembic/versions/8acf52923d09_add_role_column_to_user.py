"""Add role column to user

Revision ID: 8acf52923d09
Revises: 
Create Date: 2025-05-14 15:40:02.501401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8acf52923d09'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# If you have an Enum in your code, define it here too
role_enum = sa.Enum('User', 'Admin', name='userrole')

def upgrade() -> None:
    # For SQLite, enums are just stored as TEXT, so this works directly.
    op.add_column('user', sa.Column('role', role_enum, nullable=False, server_default='User'))


def downgrade() -> None:
    op.drop_column('user', 'role')
    role_enum.drop(op.get_bind(), checkfirst=False)