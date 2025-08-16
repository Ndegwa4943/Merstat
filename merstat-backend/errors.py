from flask import jsonify, current_app
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify({"success": False, "errors": err.messages}), 400

    @app.errorhandler(HTTPException)
    def handle_http(err):
        return jsonify({"success": False, "error": err.description}), err.code

    @app.errorhandler(Exception)
    def handle_generic(err):
        current_app.logger.exception(err)
        return jsonify({"success": False, "error": "Internal server error"}), 500
