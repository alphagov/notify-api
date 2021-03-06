"""empty message

Revision ID: 150_add_filename_to_job
Revises: 140_add_desc_to_notification
Create Date: 2015-10-30 14:58:41.262911

"""

# revision identifiers, used by Alembic.
revision = '150_add_filename_to_job'
down_revision = '140_add_desc_to_notification'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('filename', sa.String(length=255), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'filename')
    ### end Alembic commands ###
