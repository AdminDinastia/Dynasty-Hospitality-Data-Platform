"""add accommodation_id and cascade delete to uploads

Revision ID: 6b37f8922fb4
Revises: 9e706332708b
Create Date: 2026-07-02 11:44:33.942391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6b37f8922fb4"
down_revision: Union[str, Sequence[str], None] = "9e706332708b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "uploads", sa.Column("accommodation_id", sa.Integer(), nullable=False)
    )
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


def downgrade() -> None:
    op.drop_constraint("uploads_accommodation_id_fkey", "uploads", type_="foreignkey")
    op.drop_constraint("uploads_org_id_fkey", "uploads", type_="foreignkey")
    op.create_foreign_key(
        "uploads_org_id_fkey", "uploads", "organizations", ["org_id"], ["org_id"]
    )
    op.drop_column("uploads", "accommodation_id")
