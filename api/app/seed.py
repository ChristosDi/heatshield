"""Seed fictional cooling centres for the HeatShield application."""

from flask.cli import with_appcontext

import click

from .areas.models import Area
from .centres.models import CoolingCentre
from .extensions import db

@click.command("seed-centres")
@with_appcontext
def seed_centres():
    """Create fictional cooling centres without duplicating existing records."""

    centres = [
        ("HeatShield Central", "Bolton", 20, "open"),
        ("HeatShield Community", "Farnworth", 15, "open"),
        ("HeatShield North", "Bolton", 10, "closed"),
    ]

    created = 0
    skipped = 0

    try:
        for name, area_name, capacity, status in centres:

            # Retrieve or create the required area.
            area = Area.query.filter_by(name=area_name).first()

            if area is None:
                area = Area(name=area_name)
                db.session.add(area)
                db.session.flush()

            # Avoid creating duplicate cooling centres.
            existing = CoolingCentre.query.filter_by(
                name=name,
                area_id=area.id
            ).first()

            if existing is not None:
                skipped += 1
                continue

            centre = CoolingCentre(
                name=name,
                location=area_name,
                capacity=capacity,
                status=status,
                area_id=area.id
            )

            db.session.add(centre)
            created += 1

        db.session.commit()

    except Exception as error:
        db.session.rollback()
        raise click.ClickException(
            f"Unable to seed cooling centres: {error}"
        ) from error

    click.echo(f"Centres created: {created}")
    click.echo(f"Existing centres skipped: {skipped}")