"""add cascade delete to sharing consent

Revision ID: 28d6ac3e94fd
Revises: 557c86840151
Create Date: 2026-06-20 09:13:16.254122

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "28d6ac3e94fd"
down_revision: Union[str, Sequence[str], None] = "557c86840151"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "data_sharing_consents_accommodation_id_fkey",
        "data_sharing_consents",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "data_sharing_consents_accommodation_id_fkey",
        "data_sharing_consents",
        "accommodations",
        ["accommodation_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "data_sharing_consents_accommodation_id_fkey",
        "data_sharing_consents",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "data_sharing_consents_accommodation_id_fkey",
        "data_sharing_consents",
        "accommodations",
        ["accommodation_id"],
        ["id"],
    )  #
