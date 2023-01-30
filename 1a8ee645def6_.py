"""empty message

Revision ID: 1a8ee645def6
Revises: 127682c11a74
Create Date: 2014-09-28 18:41:13.168379

"""

# revision identifiers, used by Alembic.
revision = '1a8ee645def6'
down_revision = '127682c11a74'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('category', sa.Column('hidden', sa.Boolean(), nullable=True))
    op.add_column('tag', sa.Column('hidden', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tag', 'hidden')
    op.drop_column('category', 'hidden')
    ### end Alembic commands ###
