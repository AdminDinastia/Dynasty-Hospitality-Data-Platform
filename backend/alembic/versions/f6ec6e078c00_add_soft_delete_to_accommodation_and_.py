"""add soft delete to accommodation and uploads

Revision ID: f6ec6e078c00
Revises: 6b37f8922fb4
Create Date: 2026-07-06 10:43:52.894848

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f6ec6e078c00"
down_revision: Union[str, Sequence[str], None] = "6b37f8922fb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "accommodations",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "accommodations",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "uploads",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "uploads", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.drop_constraint("uploads_accommodation_id_fkey", "uploads", type_="foreignkey")
    op.drop_constraint("uploads_org_id_fkey", "uploads", type_="foreignkey")
    op.create_foreign_key(
        "uploads_accommodation_id_fkey",
        "uploads",
        "accommodations",
        ["accommodation_id"],
        ["id"],
    )
    op.create_foreign_key(
        "uploads_org_id_fkey", "uploads", "organizations", ["org_id"], ["org_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uploads_accommodation_id_fkey", "uploads", type_="foreignkey")
    op.drop_constraint("uploads_org_id_fkey", "uploads", type_="foreignkey")
    op.create_foreign_key(
        "uploads_org_id_fkey",
        "uploads",
        "organizations",
        ["org_id"],
        ["org_id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "uploads_accommodation_id_fkey",
        "uploads",
        "accommodations",
        ["accommodation_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.drop_column("uploads", "deleted_at")
    op.drop_column("uploads", "is_active")
    op.drop_column("accommodations", "deleted_at")
    op.drop_column("accommodations", "is_active")
