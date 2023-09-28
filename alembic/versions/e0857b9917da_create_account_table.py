"""create account table

Revision ID: e0857b9917da
Revises: 83a1f9c468e1
Create Date: 2023-09-27 21:16:14.100340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0857b9917da'
down_revision: Union[str, None] = '83a1f9c468e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
