"""unify product status for raw and aggregated products

Revision ID: 388108e59c24
Revises: d96fbe718959
Create Date: 2026-08-14 12:03:14.402701

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "388108e59c24"
down_revision: Union[str, Sequence[str], None] = "d96fbe718959"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE TYPE productstatus AS ENUM ('draft', 'processing', 'active', 'failed')"
    )

    op.execute("ALTER TABLE raw_products ALTER COLUMN status DROP DEFAULT")

    op.execute(
        "ALTER TABLE raw_products ALTER COLUMN status TYPE productstatus USING status::text::productstatus"
    )
    op.execute(
        "ALTER TABLE aggregated_products ALTER COLUMN status TYPE productstatus USING status::text::productstatus"
    )

    op.execute(
        "ALTER TABLE raw_products ALTER COLUMN status SET DEFAULT 'draft'::productstatus"
    )

    op.execute("DROP TYPE rawproductstatus")
    op.execute("DROP TYPE aggregatedproductstatus")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("CREATE TYPE rawproductstatus AS ENUM ('draft', 'active', 'failed')")
    op.execute(
        "CREATE TYPE aggregatedproductstatus AS ENUM ('draft', 'active', 'failed')"
    )

    op.execute("ALTER TABLE raw_products ALTER COLUMN status DROP DEFAULT")

    op.execute(
        "ALTER TABLE raw_products ALTER COLUMN status TYPE rawproductstatus USING status::text::rawproductstatus"
    )
    op.execute(
        "ALTER TABLE aggregated_products ALTER COLUMN status TYPE aggregatedproductstatus USING status::text::aggregatedproductstatus"
    )

    op.execute(
        "ALTER TABLE raw_products ALTER COLUMN status SET DEFAULT 'draft'::rawproductstatus"
    )

    op.execute("DROP TYPE productstatus")
