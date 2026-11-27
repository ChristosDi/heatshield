"""AI adapter: one interface with a Fake version (recorded fixtures) and an optional Real one.

It sits outside the Flask app and only makes suggestions. Never import anything from the app package
here, because the adapter has no database access. It is sent the request description only, never
resident details.
"""
import os

from .base import AiConfigError, AiUnavailable, Suggestion
from .fake import FakeAdapter
from .real import RealAdapter

# What the rest of HeatShield imports from here.
__all__ = ["AiConfigError", "AiUnavailable", "FakeAdapter", "RealAdapter", "Suggestion", "get_adapter"]


def get_adapter():
    """Return the AI chosen by AI_MODE in .env: "fake" (also when it is not set) or "real"."""
    mode = os.environ.get("AI_MODE", "").strip().lower() or "fake"

    if mode == "fake":
        return FakeAdapter()

    if mode == "real":
        return RealAdapter(
            base_url=read_setting("AI_BASE_URL"),
            model=read_setting("AI_MODEL"),
            api_key=read_setting("AI_API_KEY"),
        )

    raise AiConfigError('AI_MODE must be "fake" or "real"')


def read_setting(name):
    """Return one setting from .env, or stop with a message that names it (never its value)."""
    value = os.environ.get(name, "").strip()
    if not value:
        raise AiConfigError(f"{name} is missing from .env")
    return value