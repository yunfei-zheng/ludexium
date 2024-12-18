"""empty message

Revision ID: 510eac0265cd
Revises: c695aca51348
Create Date: 2024-12-17 22:46:03.685725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '510eac0265cd'
down_revision = 'c695aca51348'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('game', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    # ### end Alembic commands ###
