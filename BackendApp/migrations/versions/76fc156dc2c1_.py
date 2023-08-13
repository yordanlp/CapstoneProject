"""empty message

Revision ID: 76fc156dc2c1
Revises: 2f67d62a9f82
Create Date: 2023-08-13 11:31:59.387906

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76fc156dc2c1'
down_revision = '2f67d62a9f82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_images', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_image_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'images', ['parent_image_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_images', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('parent_image_id')

    # ### end Alembic commands ###
