"""second migration

Revision ID: b451bb2059d6
Revises: e0857b9917da
Create Date: 2023-09-27 21:37:42.404309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b451bb2059d6'
down_revision: Union[str, None] = 'e0857b9917da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
