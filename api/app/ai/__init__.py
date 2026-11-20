"""AI adapter: one interface with a Fake version (recorded fixtures) and an optional Real one.

It only makes suggestions. Never import app.extensions or any models here, because the adapter has
no database access. It is sent the request description only, never resident details.
"""
