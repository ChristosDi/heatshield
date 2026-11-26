
"""Fixed the database to match the ERD

Revision ID: cb354b182d06
Revises: 06fb73260841
"""

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = 'cb354b182d06'
down_revision = '06fb73260841'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    existing_tables = inspector.get_table_names()

    # Create areas only if it does not already exist.
    if 'areas' not in existing_tables:
        op.create_table(
            'areas',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.PrimaryKeyConstraint('id', name='pk_areas')
        )

    # Create residents only if it does not already exist.
    if 'residents' not in existing_tables:
        op.create_table(
            'residents',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('display_name', sa.String(length=100), nullable=False),
            sa.Column('contact_phone', sa.String(length=20), nullable=True),
            sa.Column('postcode', sa.String(length=10), nullable=True),
            sa.PrimaryKeyConstraint('id', name='pk_residents')
        )

    # Drop bookings if it exists, as in the original migration.
    if 'bookings' in existing_tables:
        op.drop_table('bookings')

    # Update cooling centres.
    with op.batch_alter_table('cooling_centres') as batch_op:
        batch_op.add_column(
            sa.Column('status', sa.String(length=20), nullable=False,
                      server_default='open')
        )
        batch_op.add_column(
            sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True)
        )
        batch_op.add_column(
            sa.Column('area_id', sa.Integer(), nullable=True)
        )

        batch_op.create_foreign_key(
            'fk_cooling_centres_area_id_areas',
            'areas',
            ['area_id'],
            ['id']
        )

        batch_op.drop_column('is_open')

    # Update support requests.
    with op.batch_alter_table('support_requests') as batch_op:
        batch_op.add_column(
            sa.Column('reference', sa.String(length=50), nullable=True)
        )
        batch_op.add_column(
            sa.Column('operational_priority', sa.String(length=20),
                      nullable=True)
        )
        batch_op.add_column(
            sa.Column('resident_id', sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column('area_id', sa.Integer(), nullable=True)
        )

        batch_op.drop_column('area')
        batch_op.drop_column('priority')
        batch_op.drop_column('updated_at')

    # Populate reference values for existing requests.
    rows = connection.execute(
        sa.text(
            "SELECT id FROM support_requests WHERE reference IS NULL"
        )
    ).fetchall()

    for row in rows:
        connection.execute(
            sa.text(
                "UPDATE support_requests "
                "SET reference = :reference WHERE id = :id"
            ),
            {
                'reference': f"HS-{uuid.uuid4().hex[:12].upper()}",
                'id': row.id
            }
        )

    # Enforce required fields and uniqueness.
    with op.batch_alter_table('support_requests') as batch_op:
        batch_op.alter_column(
            'reference',
            existing_type=sa.String(length=50),
            nullable=False
        )
        batch_op.alter_column(
            'operational_priority',
            existing_type=sa.String(length=20),
            nullable=False,
            server_default='medium'
        )
        batch_op.create_unique_constraint(
            'uq_support_requests_reference',
            ['reference']
        )


def downgrade():
    raise NotImplementedError(
        "This migration cannot safely be reversed automatically."
    )
