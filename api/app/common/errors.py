"""One JSON error format for every route.

flask-smorest already returns HTTP errors as JSON. Add handlers here only for errors it does not cover.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_http_error(error):

        return jsonify({
            "status": error.name,
            "code": error.code,
            "message": error.description
        }), error.code