
"""Add support_requests.reference column back

Revision ID: df121040af24
Revises: e22dc5273961
"""

import uuid

from alembic import op
import sqlalchemy as sa


revision = "df121040af24"
down_revision = "e22dc5273961"
branch_labels = None
depends_on = None


def upgrade():
    # Add the reference column as nullable initially.
    with op.batch_alter_table("support_requests") as batch_op:
        batch_op.add_column(
            sa.Column("reference", sa.String(length=50), nullable=True)
        )

    # Generate unique references for existing requests.
    connection = op.get_bind()

    rows = connection.execute(
        sa.text("SELECT id FROM support_requests")
    ).fetchall()

    for row in rows:
        reference = f"HS-{uuid.uuid4().hex[:12].upper()}"

        connection.execute(
            sa.text("""
                UPDATE support_requests
                SET reference = :reference
                WHERE id = :id
            """),
            {"reference": reference, "id": row.id},
        )

    # Enforce NOT NULL and uniqueness.
    with op.batch_alter_table("support_requests") as batch_op:
        batch_op.alter_column(
            "reference",
            existing_type=sa.String(length=50),
            nullable=False,
        )

        batch_op.create_unique_constraint(
            "uq_support_requests_reference",
            ["reference"],
        )


def downgrade():
    with op.batch_alter_table("support_requests") as batch_op:
        batch_op.drop_constraint(
            "uq_support_requests_reference",
            type_="unique",
        )
        batch_op.drop_column("reference")
