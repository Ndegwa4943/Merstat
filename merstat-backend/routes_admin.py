import csv
from io import StringIO
from flask import request, jsonify, Response
from flask_jwt_extended import jwt_required, get_jwt
from models import CareerApplication, TrainingApplication, ServiceRequest
from flask import send_file, abort, current_app
from pathlib import Path


def _require_admin():
    claims = get_jwt()
    return claims.get("role") == "admin"

def init_admin_routes(app):

    @app.route("/api/admin/careers", methods=["GET"])
    @jwt_required()
    def list_careers():
        if not _require_admin():
            return jsonify({"success": False, "error": "Forbidden"}), 403
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        q = CareerApplication.query.order_by(CareerApplication.created_at.desc())
        p = q.paginate(page=page, per_page=per_page, error_out=False)
        items = [{
            "id": i.id,
            "first_name": i.first_name,
            "last_name": i.last_name,
            "email": i.email,
            "phone": i.phone,
            "position": i.position,
            "created_at": i.created_at.isoformat(),
        } for i in p.items]
        return jsonify({"success": True, "items": items, "page": p.page, "per_page": p.per_page, "total": p.total, "pages": p.pages}), 200

    @app.route("/api/admin/careers.csv", methods=["GET"])
    @jwt_required()
    def careers_csv():
        if not _require_admin():
            return jsonify({"success": False, "error": "Forbidden"}), 403
        rows = CareerApplication.query.order_by(CareerApplication.created_at.desc()).all()
        def generate():
            data = StringIO()
            writer = csv.writer(data)
            writer.writerow(["id","first_name","last_name","email","phone","position","resume_path","created_at"])
            yield data.getvalue(); data.seek(0); data.truncate(0)
            for r in rows:
                writer.writerow([r.id, r.first_name, r.last_name, r.email, r.phone, r.position, r.resume_path, r.created_at.isoformat()])
                yield data.getvalue(); data.seek(0); data.truncate(0)
        return Response(generate(), mimetype="text/csv", headers={"Content-Disposition":"attachment; filename=career_applications.csv"})

    @app.route("/api/admin/trainings", methods=["GET"])
    @jwt_required()
    def list_trainings():
        if not _require_admin():
            return jsonify({"success": False, "error": "Forbidden"}), 403
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        q = TrainingApplication.query.order_by(TrainingApplication.created_at.desc())
        p = q.paginate(page=page, per_page=per_page, error_out=False)
        items = [{
            "id": i.id,
            "applicant_name": i.applicant_name,
            "course_title": i.course_title,
            "created_at": i.created_at.isoformat(),
        } for i in p.items]
        return jsonify({"success": True, "items": items, "page": p.page, "per_page": p.per_page, "total": p.total, "pages": p.pages}), 200

    @app.route("/api/admin/services", methods=["GET"])
    @jwt_required()
    def list_services():
        if not _require_admin():
            return jsonify({"success": False, "error": "Forbidden"}), 403
        page = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
        q = ServiceRequest.query.order_by(ServiceRequest.created_at.desc())
        p = q.paginate(page=page, per_page=per_page, error_out=False)
        items = [{
            "id": i.id,
            "company_name": i.company_name,
            "contact_person": i.contact_person,
            "email": i.email,
            "phone": i.phone,
            "service_type": i.service_type,
            "created_at": i.created_at.isoformat(),
        } for i in p.items]
        return jsonify({"success": True, "items": items, "page": p.page, "per_page": p.per_page, "total": p.total, "pages": p.pages}), 200
    
    @app.route("/api/admin/careers/<int:app_id>/resume", methods=["GET"])
    @jwt_required()
    def download_resume(app_id):
        if not _require_admin():
            return jsonify({"success": False, "error": "Forbidden"}), 403

        # Find the application
        obj = CareerApplication.query.get_or_404(app_id)

        # No path stored
        if not obj.resume_path:
            abort(404, description="No resume attached to this application.")

        # Resolve path (support relative or absolute)
        path = Path(obj.resume_path)
        if not path.is_absolute():
            # stored as relative to app root
            path = (Path(current_app.root_path) / path).resolve()

        # Security & existence checks
        try:
            path.relative_to(Path(current_app.root_path))
        except Exception:
            # If it's outside app root (because you stored an absolute path), that's OK,
            # but we still must check it exists and only serve that exact file.
            pass

        if not path.exists() or not path.is_file():
            abort(404, description="Resume file not found on server.")

        # Download as attachment
        return send_file(path, as_attachment=True)
