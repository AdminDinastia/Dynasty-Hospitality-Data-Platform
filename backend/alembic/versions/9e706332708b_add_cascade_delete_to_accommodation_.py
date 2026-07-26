"""add cascade delete to accommodation events

Revision ID: 9e706332708b
Revises: c2ba975194f4
Create Date: 2026-07-01 16:37:12.241333

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9e706332708b"
down_revision: Union[str, Sequence[str], None] = "c2ba975194f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "accommodation_events_accommodation_id_fkey",
        "accommodation_events",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "accommodation_events_accommodation_id_fkey",
        "accommodation_events",
        "accommodations",
        ["accommodation_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "capacity_changes_event_id_fkey", "capacity_changes", type_="foreignkey"
    )
    op.create_foreign_key(
        "capacity_changes_event_id_fkey",
        "capacity_changes",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
        ondelete="CASCADE",
    )

    op.drop_constraint(
        "category_changes_event_id_fkey", "category_changes", type_="foreignkey"
    )
    op.create_foreign_key(
        "category_changes_event_id_fkey",
        "category_changes",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("renovations_event_id_fkey", "renovations", type_="foreignkey")
    op.create_foreign_key(
        "renovations_event_id_fkey",
        "renovations",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
        ondelete="CASCADE",
    )

    op.drop_constraint("type_changes_event_id_fkey", "type_changes", type_="foreignkey")
    op.create_foreign_key(
        "type_changes_event_id_fkey",
        "type_changes",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("type_changes_event_id_fkey", "type_changes", type_="foreignkey")
    op.create_foreign_key(
        "type_changes_event_id_fkey",
        "type_changes",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
    )

    op.drop_constraint("renovations_event_id_fkey", "renovations", type_="foreignkey")
    op.create_foreign_key(
        "renovations_event_id_fkey",
        "renovations",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
    )

    op.drop_constraint(
        "category_changes_event_id_fkey", "category_changes", type_="foreignkey"
    )
    op.create_foreign_key(
        "category_changes_event_id_fkey",
        "category_changes",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
    )

    op.drop_constraint(
        "capacity_changes_event_id_fkey", "capacity_changes", type_="foreignkey"
    )
    op.create_foreign_key(
        "capacity_changes_event_id_fkey",
        "capacity_changes",
        "accommodation_events",
        ["event_id"],
        ["event_id"],
    )

    op.drop_constraint(
        "accommodation_events_accommodation_id_fkey",
        "accommodation_events",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "accommodation_events_accommodation_id_fkey",
        "accommodation_events",
        "accommodations",
        ["accommodation_id"],
        ["id"],
    )
