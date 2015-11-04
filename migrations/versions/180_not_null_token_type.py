"""empty message

Revision ID: 180_not_null_token_type
Revises: 170_token_type
Create Date: 2015-11-02 12:29:52.320991

"""

# revision identifiers, used by Alembic.
revision = '180_not_null_token_type'
down_revision = '170_token_type'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token', 'type',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('token', 'type',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    ### end Alembic commands ###