"""Add hotel_room column to badge_to_room_night

Revision ID: f60794f1f9fd
Revises: 9595449dcb38
Create Date: 2019-11-20 23:05:58.763619

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f60794f1f9fd'
down_revision = '9595449dcb38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('badge_to_room_night', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'hotel_room', ['hotel_room'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('badge_to_room_night', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
