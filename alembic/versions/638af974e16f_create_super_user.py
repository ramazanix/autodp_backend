"""Create super_user

Revision ID: 638af974e16f
Revises: 99d9e8ba1d28
Create Date: 2023-06-02 16:27:18.904934

"""
from alembic import op
import sqlalchemy as sa
from src import settings
from uuid import uuid4
from datetime import datetime
from src.security import get_password_hash

# revision identifiers, used by Alembic.
revision = "638af974e16f"
down_revision = "99d9e8ba1d28"
branch_labels = None
depends_on = None


def upgrade() -> None:
    super_user_password = get_password_hash(settings.SUPER_USER_PASSWORD)
    time_now = datetime.now()
    query = (
        f"INSERT INTO users (id, username, hashed_password, role_id, created_at, updated_at) values ('{uuid4()}', "
        f"'super_user', '{super_user_password}', (select id FROM roles WHERE name='admin'), '{time_now}', '{time_now}')"
    )
    op.execute(query)


def downgrade() -> None:
    query = 'DELETE FROM users where username = "super_user"'
    op.execute(query)
