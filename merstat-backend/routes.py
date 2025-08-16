from pathlib import Path
from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db, ServiceRequest, CareerApplication, TrainingApplication
from schemas import service_request_schema, career_schema, training_schema
from marshmallow import ValidationError

ALLOWED_RESUME_EXT = {"pdf", "doc", "docx"}

def _get_data():
    data = request.get_json(silent=True)
    if data is None:
        data = request.form.to_dict()
    return data

def _ensure_upload_dir(app):
    upload_dir = app.config.get("RESUME_UPLOAD_DIR", "uploads/resumes")
    full_path = Path(app.root_path) / upload_dir
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path

def _save_resume(file_storage, upload_dir_path):
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_RESUME_EXT:
        raise ValidationError({"resume": ["Resume must be a PDF, DOC, or DOCX file."]})
    dest = upload_dir_path / filename
    i = 1
    base = filename.rsplit(".", 1)[0]
    while dest.exists():
        dest = upload_dir_path / f"{base}_{i}.{ext}"
        i += 1
    file_storage.save(dest)
    return str(dest.relative_to(Path(current_app.root_path)))

def init_routes(app):

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"ok": True}), 200

    @app.route("/api/db-check", methods=["GET"])
    def db_check():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify({"ok": True, "db": "connected"}), 200
        except Exception as e:
            return jsonify({"ok": False, "db": "error", "error": str(e)}), 500

    @app.route("/api/services/request", methods=["POST"])
    def create_service_request():
        data = _get_data()
        payload = service_request_schema.load(data)
        try:
            obj = ServiceRequest(
                company_name=payload["companyName"],
                contact_person=payload["contactPerson"],
                email=payload["email"],
                phone=payload["phone"],
                service_type=payload["serviceType"],
                timeline=payload["timeline"],
                project_description=payload["projectDescription"],
                budget_range=payload.get("budgetRange"),
            )
            db.session.add(obj)
            db.session.commit()
            return jsonify({"success": True, "id": obj.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/careers/apply", methods=["POST"])
    def careers_apply():
        data = _get_data()
        payload = career_schema.load(data)
        try:
            resume_path = payload.get("resumePath")
            if "resume" in request.files:
                upload_dir = _ensure_upload_dir(app)
                resume_path = _save_resume(request.files["resume"], upload_dir)
            if not resume_path:
                raise ValidationError({"resume": ["Resume is required (file or resumePath)."]})
            obj = CareerApplication(
                first_name=payload["firstName"],
                last_name=payload["lastName"],
                email=payload["email"],
                phone=payload.get("phone"),
                position=payload["position"],
                resume_path=resume_path,
                message=payload.get("message"),
            )
            db.session.add(obj)
            db.session.commit()
            return jsonify({"success": True, "id": obj.id}), 201
        except ValidationError as ve:
            db.session.rollback()
            raise ve
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/trainings/apply", methods=["POST"])
    def trainings_apply():
        data = _get_data()
        payload = training_schema.load(data)
        try:
            obj = TrainingApplication(
                course_title=payload["courseTitle"],
                application_date=payload["applicationDate"],
                course_code=payload["courseCode"],
                course_start_date=payload["courseStartDate"],
                course_end_date=payload["courseEndDate"],
                applicant_name=payload["applicantName"],
                sex=payload["sex"],
                dob=payload["dob"],
                nationality=payload["nationality"],
                passport_id=payload["passportId"],
                date_of_issue=payload["dateOfIssue"],
                employer=payload["employer"],
                contact_address=payload["contactAddress"],
                emergency_contact=payload["emergencyContact"],
                education_background=payload["educationBackground"],
                present_position=payload["presentPosition"],
                present_post_date=payload["presentPostDate"],
                present_duties=payload["presentDuties"],
                course_reason=payload["courseReason"],
                special_request=payload.get("specialRequest"),
                course_info_source=payload["courseInfoSource"],
                sponsorship=payload.get("sponsorship"),
                sponsoring_agent=payload.get("sponsoringAgent"),
                sponsoring_address=payload.get("sponsoringAddress"),
                contact_person_title=payload.get("contactPersonTitle"),
                contact_person_name=payload.get("contactPersonName"),
                contact_person_phone=payload.get("contactPersonPhone"),
                contact_person_email=payload.get("contactPersonEmail"),
            )
            db.session.add(obj)
            db.session.commit()
            return jsonify({"success": True, "id": obj.id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 500
