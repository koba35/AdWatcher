"""start

Revision ID: 48e9e5b25e0
Revises: 
Create Date: 2015-10-19 18:02:24.148788

"""

# revision identifiers, used by Alembic.
revision = '48e9e5b25e0'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('core',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('last_visit', sa.DateTime(), nullable=True),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('spamers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('spamers')
    op.drop_table('core')
    ### end Alembic commands ###
