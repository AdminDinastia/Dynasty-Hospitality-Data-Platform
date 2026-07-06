"""add creation events table and created enum value

Revision ID: c2ba975194f4
Revises: 99c256d3e77b
Create Date: 2026-07-01 15:31:22.279915

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2ba975194f4"
down_revision: Union[str, Sequence[str], None] = "99c256d3e77b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE eventtype ADD VALUE IF NOT EXISTS 'created'")
    op.create_table(
        "creation_events",
        sa.Column(
            "event_id",
            sa.Integer(),
            sa.ForeignKey("accommodation_events.event_id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "initial_type",
            sa.Enum(
                "hotel",
                "hostel",
                "aparthotel",
                "resort",
                name="accommodationtype",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "initial_category_system",
            sa.Enum("stars", "keys", name="categorysystem", create_type=False),
            nullable=False,
        ),
        sa.Column("initial_category_value", sa.Float(), nullable=False),
        sa.Column("initial_room_count", sa.Integer(), nullable=False),
    )
    op.alter_column(
        "category_changes",
        "old_value",
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        existing_nullable=False,
    )
    op.alter_column(
        "category_changes",
        "new_value",
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS creation_events")
    op.execute("DELETE FROM accommodation_events WHERE event_type = 'created'")
    op.execute(
        "ALTER TABLE accommodation_events ALTER COLUMN event_type TYPE varchar USING event_type::text"
    )
    op.execute("DROP TYPE eventtype")
    op.execute(
        "CREATE TYPE eventtype AS ENUM ('renovation', 'category_change', 'capacity_change', 'type_change')"
    )
    op.execute(
        "ALTER TABLE accommodation_events ALTER COLUMN event_type TYPE eventtype USING event_type::text::eventtype"
    )
    op.alter_column(
        "category_changes",
        "new_value",
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.alter_column(
        "category_changes",
        "old_value",
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
