"""HeatShield Flask API: the application factory."""
from flask import Flask
from flask_smorest import Api

from .config import Config
from .extensions import api, db, migrate
from .requests.routes import blp as requests_blp
from .reports.routes import blp as reports_blp
from .bookings.routes import blp as bookings_blp
from .common.errors import register_error_handlers


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
    from .centres import models as _centres  # noqa: F401
    from .escalations import models as _escalations  # noqa: F401
    from .requests import models as _requests  # noqa: F401
    from .triage import models as _triage  # noqa: F401
    from .bookings import models as _bookings
    
    # Register error handlers
    register_error_handlers(app)


    # Register each feature's blueprint here when its first route is added, for example:
    #     from .requests.routes import blp as requests_blp
    #     api.register_blueprint(requests_blp)
    api.register_blueprint(requests_blp)
    api.register_blueprint(reports_blp)
    api.register_blueprint(bookings_blp)
    

    return app
