from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.now(datetime.timezone.utc), onupdate=datetime.now(datetime.timezone.utc), nullable=False
    )


# ---------- BOOK US (Service Request) ----------
class ServiceRequest(db.Model, TimestampMixin):
    __tablename__ = "service_requests"

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(32), nullable=False)

    # Monitoring and Evaluation | Research and Statistics | Capacity Building
    service_type = db.Column(db.String(80), nullable=False)

    timeline = db.Column(db.String(120), nullable=False)  # free text like "3 months"
    project_description = db.Column(db.Text, nullable=False)
    budget_range = db.Column(db.String(120))  # optional free text


# ---------- CAREERS ----------
class CareerApplication(db.Model, TimestampMixin):
    __tablename__ = "career_applications"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(160), nullable=False, index=True)
    phone = db.Column(db.String(32))

    # Data Analysis | Software Development | Business Development | Procurement | Other
    position = db.Column(db.String(120), nullable=False)

    # We’ll store a path or URL to the uploaded resume
    resume_path = db.Column(db.String(512), nullable=False)

    message = db.Column(db.Text)  # optional cover/notes


# ---------- TRAINING APPLICATION ----------
class TrainingApplication(db.Model, TimestampMixin):
    __tablename__ = "training_applications"

    id = db.Column(db.Integer, primary_key=True)

    # Course meta
    course_title = db.Column(db.String(200), nullable=False)
    application_date = db.Column(db.Date, nullable=False)
    course_code = db.Column(db.String(80), nullable=False)
    course_start_date = db.Column(db.Date, nullable=False)
    course_end_date = db.Column(db.Date, nullable=False)

    # Applicant bio
    applicant_name = db.Column(db.String(160), nullable=False)
    sex = db.Column(db.String(20), nullable=False)  # free text from form
    dob = db.Column(db.Date, nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    passport_id = db.Column(db.String(80), nullable=False)
    date_of_issue = db.Column(db.Date, nullable=False)

    # Work & contact
    employer = db.Column(db.String(200), nullable=False)
    contact_address = db.Column(db.Text, nullable=False)
    emergency_contact = db.Column(db.Text, nullable=False)

    # Education & current role
    education_background = db.Column(db.Text, nullable=False)
    present_position = db.Column(db.String(160), nullable=False)
    present_post_date = db.Column(db.Date, nullable=False)
    present_duties = db.Column(db.Text, nullable=False)

    # Motivation & special requests
    course_reason = db.Column(db.Text, nullable=False)
    special_request = db.Column(db.Text)  # optional

    # Source & sponsorship
    course_info_source = db.Column(db.String(200), nullable=False)
    sponsorship = db.Column(db.String(20))  # "self" | "other"
    sponsoring_agent = db.Column(db.String(200))
    sponsoring_address = db.Column(db.String(300))

    # Sponsor contact
    contact_person_title = db.Column(db.String(120))
    contact_person_name = db.Column(db.String(160))
    contact_person_phone = db.Column(db.String(40))
    contact_person_email = db.Column(db.String(160))


# Helper: safely parse ISO date strings from form or JSON
def parse_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        # Accept YYYY-MM-DD from <input type="date">
        return datetime.strptime(value, "%Y-%m-%d").date()
    except Exception:
        return None
