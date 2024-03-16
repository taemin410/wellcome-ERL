"""add foreign keys

Revision ID: 8a2ff368161c
Revises: 0cffe98964a1
Create Date: 2024-03-16 12:47:49.299306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a2ff368161c'
down_revision: Union[str, None] = '0cffe98964a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('education', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'education', 'user', ['user_id'], ['id'])
    op.add_column('experience', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'experience', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'experience', type_='foreignkey')
    op.drop_column('experience', 'user_id')
    op.drop_constraint(None, 'education', type_='foreignkey')
    op.drop_column('education', 'user_id')
    # ### end Alembic commands ###
