"""empty message

Revision ID: 60_add_active_and_limit
Revises: 50_added_sender_id
Create Date: 2015-10-20 11:05:12.343633

"""

# revision identifiers, used by Alembic.
revision = '60_add_active_and_limit'
down_revision = '50_added_sender_id'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('services', sa.Column('active', sa.Boolean(), nullable=False))
    op.add_column('services', sa.Column('limit', sa.BigInteger(), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('services', 'limit')
    op.drop_column('services', 'active')
    ### end Alembic commands ###
