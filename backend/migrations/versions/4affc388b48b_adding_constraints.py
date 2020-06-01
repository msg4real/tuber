"""Adding constraints

Revision ID: 4affc388b48b
Revises: e3921de45eb5
Create Date: 2020-01-20 20:42:16.965622

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4affc388b48b'
down_revision = 'e3921de45eb5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('grant', schema=None) as batch_op:
        batch_op.create_foreign_key("grant_user_fkey", 'user', ['user'], ['id'])

    with op.batch_alter_table('room_night_approval', schema=None) as batch_op:
        batch_op.alter_column('badge',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('room_night_approval', schema=None) as batch_op:
        batch_op.alter_column('badge',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('grant', schema=None) as batch_op:
        batch_op.drop_constraint("grant_user_fkey", type_='foreignkey')

    # ### end Alembic commands ###
