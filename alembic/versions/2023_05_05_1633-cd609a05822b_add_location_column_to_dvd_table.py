"""Add location column to DVD table

Revision ID: cd609a05822b
Revises: 
Create Date: 2023-05-05 16:33:02.695683

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.models import DEFAULT_LOCATION_TYPE, LocationTypeEnum


# revision identifiers, used by Alembic.
revision = 'cd609a05822b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    location = postgresql.ENUM(LocationTypeEnum, name='location')
    location.create(op.get_bind(), checkfirst=True)
    op.add_column('DVD', sa.Column('location', location, nullable=False, default=DEFAULT_LOCATION_TYPE, server_default=DEFAULT_LOCATION_TYPE.value))

def downgrade() -> None:
    op.drop_column('DVD', 'location')
