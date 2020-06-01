"""Adding active column to email_source

Revision ID: 0f768e57a051
Revises: fc8aad836b90
Create Date: 2019-11-23 02:48:10.414987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f768e57a051'
down_revision = 'fc8aad836b90'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('badge', schema=None) as batch_op:
        batch_op.alter_column('user',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('email_source', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('email_source', schema=None) as batch_op:
        batch_op.drop_column('active')

    with op.batch_alter_table('badge', schema=None) as batch_op:
        batch_op.alter_column('user',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
