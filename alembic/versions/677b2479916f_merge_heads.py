"""merge heads

Revision ID: 677b2479916f
Revises: 80c79431a520, d448e4eefca2
Create Date: 2026-01-07 01:19:40.352842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '677b2479916f'
down_revision: Union[str, None] = ('80c79431a520', 'd448e4eefca2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
