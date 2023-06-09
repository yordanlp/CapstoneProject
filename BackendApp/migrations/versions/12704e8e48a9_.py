"""empty message

Revision ID: 12704e8e48a9
Revises: 09b609f7c681
Create Date: 2023-07-08 22:13:52.312629

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12704e8e48a9'
down_revision = '09b609f7c681'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('model', sa.String(length=30), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('images', schema=None) as batch_op:
        batch_op.drop_column('model')

    # ### end Alembic commands ###
