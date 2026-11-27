"""HeatShield Flask API: the application factory."""
from flask import Flask

from .areas.routes import blp as areas_blp
from .bookings.routes import blp as bookings_blp
from .centres.routes import blp as centres_blp
from .common.errors import register_error_handlers
from .config import Config
from .extensions import api, db, migrate
from .reports.routes import blp as reports_blp
from .requests.routes import blp as requests_blp
from .residents.routes import blp as residents_blp
from .seed import seed_centres
from .volunteers.routes import blp as volunteers_blp
from .welfare_visits.routes import blp as welfare_visits_blp


def create_app(test_config=None):
    """Create and configure the app. Tests can pass their own settings in test_config."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    # Batch mode lets migrations change existing tables in SQLite.
    migrate.init_app(app, db, render_as_batch=True)
    api.init_app(app)

    # Import every feature's models so Flask-Migrate sees all the tables.
    from .areas import models as _areas  # noqa: F401
    from .audit import models as _audit  # noqa: F401
    from .bookings import models as _bookings  # noqa: F401
    from .centres import models as _centres  # noqa: F401
    from .duplicates import models as _duplicates  # noqa: F401
    from .escalations import models as _escalations  # noqa: F401
    from .heatwave_sessions import models as _heatwage_sessions  # noqa: F401
    from .heatwave_sessions import models as _heatwave_sessions  # noqa: F401
    from .requests import models as _requests  # noqa: F401
    from .residents import models as _residents  # noqa: F401  <-- ADD THIS
    from .triage import models as _triage  # noqa: F401
    from .welfare_visits import models as _welfare_visits  # noqa: F401
    
    # Register error handlers
    register_error_handlers(app)

    # KEEP THIS LIST ORDERED ALPHABETICALLY - Saad 
    # Register each feature's blueprint here
    api.register_blueprint(areas_blp)
    api.register_blueprint(bookings_blp)
    api.register_blueprint(centres_blp)
    api.register_blueprint(reports_blp)
    api.register_blueprint(requests_blp)
    api.register_blueprint(residents_blp)
    api.register_blueprint(volunteers_blp)
    api.register_blueprint(welfare_visits_blp)

    # Register the fictional cooling-centre seed command.
    app.cli.add_command(seed_centres)

    return app