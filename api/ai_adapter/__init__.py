"""AI adapter: one interface with a Fake version (recorded fixtures) and an optional Real one.

It sits outside the Flask app and only makes suggestions. Never import anything from the app package
here, because the adapter has no database access. It is sent the request description only, never
resident details.
"""
