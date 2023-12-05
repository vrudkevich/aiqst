"""add dt column

Revision ID: cede38ca37f4
Revises: 1dc8a5628e30
Create Date: 2023-12-04 12:15:48.515493

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'cede38ca37f4'
down_revision: Union[str, None] = '1dc8a5628e30'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('weather_data', sa.Column('dt', sa.DateTime, nullable=True), schema='source')
    op.add_column('pos_details', sa.Column('date_registered',sa.DateTime(), server_default=sa.text('now()'), nullable=False), schema='source')
    op.add_column('products', sa.Column('date_registered',sa.DateTime(), server_default=sa.text('now()'), nullable=False), schema='source')
    op.add_column('sales', sa.Column('date_registered',sa.DateTime(), server_default=sa.text('now()'), nullable=False), schema='source')
    op.add_column('weather_data', sa.Column('date_registered',sa.DateTime(), server_default=sa.text('now()'), nullable=False), schema='source')

def downgrade() -> None:
    pass
