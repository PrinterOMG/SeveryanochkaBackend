"""Add birthday to user

Revision ID: abf24f857fd8
Revises: a4588a6b43af
Create Date: 2024-01-17 16:51:57.154241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abf24f857fd8'
down_revision: Union[str, None] = 'a4588a6b43af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('birthday', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'birthday')
    # ### end Alembic commands ###
