"""initial migration

Revision ID: 1dc8a5628e30
Revises: 
Create Date: 2023-12-04 10:27:17.660939

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '1dc8a5628e30'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('date_registered', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='source'
    )
    op.create_table('pos_details',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('eff_start_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('eff_end_date', sa.DateTime(), server_default=sa.text("TO_TIMESTAMP('1900-01-01 00:00:00', 'YYYY-MM-DD HH24:MI:SS')"), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='source'
    )
    op.create_table('products',
    sa.Column('product_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('sku', sa.String(length=100), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=True),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('product_id'),
    schema='source'
    )
    op.create_table('sales',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.Column('pos_id', sa.Integer(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('qty', sa.Integer(), nullable=False),
    sa.Column('order_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['source.customers.id'], ),
    sa.ForeignKeyConstraint(['pos_id'], ['source.pos_details.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='source'
    )
    op.create_table('weather_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('pos_id', sa.Integer(), nullable=False),
    sa.Column('weather', sa.String(length=100), nullable=True),
    sa.Column('weather_des', sa.String(length=100), nullable=True),
    sa.Column('temp', sa.Float(), nullable=True),
    sa.Column('temp_feels_like', sa.Float(), nullable=True),
    sa.Column('temp_min', sa.Float(), nullable=True),
    sa.Column('temp_max', sa.Float(), nullable=True),
    sa.Column('pressure', sa.Float(), nullable=True),
    sa.Column('humidity', sa.Float(), nullable=True),
    sa.Column('visibility', sa.Float(), nullable=True),
    sa.Column('wind_speed', sa.Float(), nullable=True),
    sa.Column('wind_deg', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['pos_id'], ['source.pos_details.id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='source'
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("drop schema source")
    op.drop_table('weather_data', schema='source')
    op.drop_table('sales', schema='source')
    op.drop_table('products', schema='source')
    op.drop_table('pos_details', schema='source')
    op.drop_table('customers', schema='source')
    # ### end Alembic commands ###
