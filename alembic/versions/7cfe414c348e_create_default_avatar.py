"""Create default avatar

Revision ID: 7cfe414c348e
Revises: 83ea0581b6db
Create Date: 2023-11-20 22:29:27.524777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cfe414c348e'
down_revision = '83ea0581b6db'
branch_labels = None
depends_on = None


from alembic import op
import sqlalchemy as sa
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()


# revision identifiers, used by Alembic.
revision = "7cfe414c348e"
down_revision = "83ea0581b6db"
branch_labels = None
depends_on = None


def upgrade() -> None:
    id = uuid4()
    name = "default_avatar"
    size = os.stat(f'{os.environ["STATIC_PATH"]}/_default.png').st_size
    image_location = f'{os.environ["STATIC_PATH"]}/_default.png'
    query = (f"INSERT INTO images (id, name, size, location) VALUES ('{id}', '{name}', {size}, '{image_location}')")
    op.execute(query)

def downgrade() -> None:
    query = 'DELETE FROM images WHERE name = "default_avatar"'
    op.execute(query)
