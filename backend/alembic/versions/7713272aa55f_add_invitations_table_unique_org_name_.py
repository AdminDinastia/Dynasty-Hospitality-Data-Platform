"""add invitations table, unique org name, user active fields

Revision ID: 7713272aa55f
Revises: 66c57a36a8a2
Create Date: 2026-05-20 13:54:11.659751

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7713272aa55f"
down_revision: Union[str, Sequence[str], None] = "66c57a36a8a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "invitations",
        sa.Column("invitation_id", sa.Integer(), nullable=False),
        sa.Column("org_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "accepted", name="invitationstatus"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["organizations.org_id"],
        ),
        sa.PrimaryKeyConstraint("invitation_id"),
    )
    op.create_unique_constraint("organizations_name_key", "organizations", ["name"])
    op.add_column(
        "users",
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "users", sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "deactivated_at")
    op.drop_column("users", "is_active")
    op.drop_constraint("organizations_name_key", "organizations", type_="unique")
    op.drop_table("invitations")
