"""Add Discord info columns

Revision ID: 7a200c081912
Revises: 630d8bf7fd99
Create Date: 2026-06-23 15:52:39.683706

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7a200c081912"
down_revision: Union[str, Sequence[str], None] = "630d8bf7fd99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the columns with a temporary server_default so existing rows are
    # backfilled (SQLite refuses a NOT NULL column without a default), then
    # drop the default so the schema matches the model.
    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(
            sa.Column("discord_id", sa.String(), nullable=False, server_default="")
        )
        batch_op.add_column(
            sa.Column("discord_name", sa.String(), nullable=False, server_default="")
        )

    with op.batch_alter_table("messages") as batch_op:
        batch_op.alter_column("discord_id", server_default=None)
        batch_op.alter_column("discord_name", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_column("discord_name")
        batch_op.drop_column("discord_id")
