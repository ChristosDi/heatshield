"""One JSON error format for every route.

flask-smorest already returns HTTP errors as JSON. Add handlers here only for errors it does not cover.
"""
from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):

        return jsonify({
            "status": "Bad Request",
            "code": 400,
            "errors": error.messages
        }), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        
        return jsonify({
            "status": error.name,
            "code": error.code,
            "message": error.description
        }), error.code
        
    @app.errorhandler(422)
    def handle_unprocessable_entity(err):

        data = getattr(err, "data", None) or {}
        messages = data.get("messages", ["Invalid request"])

        return jsonify({
            "code": 400,
            "status": "Bad Request",
            "errors": messages
        }), 400  