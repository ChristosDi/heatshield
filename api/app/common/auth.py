"""Staff permission checks: 401 when not logged in, 403 when not allowed.

How Flask identifies the staff user comes from the tutor's starter project (still pending).
"""
from functools import wraps
from flask import request, jsonify


def require_authentication(func):

    @wraps(func)
    def decorated(*args, **kwargs):

        token = request.headers.get("Authorization")

        if not token:
            return jsonify({
                "message": "Authentication required"
            }), 401

        return func(*args, **kwargs)

    return decorated