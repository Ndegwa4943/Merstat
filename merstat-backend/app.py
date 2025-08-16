import os
from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
from config import Config
from models import db
from routes import init_routes
from routes_admin import init_admin_routes
from errors import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    origins = [o.strip() for o in app.config.get("FRONTEND_ORIGINS", "http://localhost:3000").split(",")]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    db.init_app(app)
    Migrate(app, db)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change-me-jwt")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
    JWTManager(app)

    init_routes(app)
    init_admin_routes(app)
    register_error_handlers(app)

    @app.post("/api/admin/login")
    def admin_login():
        from flask import request, jsonify
        user = request.json.get("user")
        pwd = request.json.get("password")
        if user and pwd:
            token = create_access_token(identity=user, additional_claims={"role": "admin"})
            return jsonify({"access_token": token})
        return jsonify({"error": "Invalid credentials"}), 401

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
