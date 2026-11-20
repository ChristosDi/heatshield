"""App settings, read from environment variables."""
import os


class Config:
    # Each developer has a local SQLite file built from the migrations.
    # A relative SQLite path is created inside the instance/ folder, which Git ignores.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///heatshield.db")

    # flask-smorest needs these three to start. The API docs page is added later.
    API_TITLE = "HeatShield API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
