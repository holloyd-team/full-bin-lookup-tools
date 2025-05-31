from __future__ import annotations

from functools import wraps
from typing import Optional

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
)

from .models import Bin, Submission
from . import db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    """Decorator to require login for admin routes."""

    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return view(**kwargs)

    return wrapped_view


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    colors = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    error: Optional[str] = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        admin_cfg = current_app.config.get("APP_CONFIG", {}).get("admin", {})
        if (
            username == admin_cfg.get("username")
            and password == admin_cfg.get("password")
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin.dashboard"))
        error = "Invalid credentials"
    return render_template("admin_login.html", error=error, colors=colors)


@admin_bp.route("/logout")
@login_required
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin.login"))


@admin_bp.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    colors = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    message: Optional[str] = None
    record: Optional[Bin] = None
    if request.method == "POST":
        action = request.form.get("action")
        bin_code = request.form.get("bin", "").strip()
        if not bin_code.isdigit() or len(bin_code) != 6:
            message = "Please enter a valid 6 digit BIN."
        elif action == "search":
            record = Bin.query.filter_by(bin=bin_code).first()
            if not record:
                message = "BIN not found. Fill the form below to create it."
        elif action == "save":
            record = Bin.query.filter_by(bin=bin_code).first()
            fields = [
                "category",
                "reloadable",
                "international",
                "max_balance",
                "company",
                "country",
                "customer_service",
                "distributor",
                "issuer",
                "type",
                "website_url",
            ]
            data = {field: request.form.get(field) or None for field in fields}
            max_balance = data.get("max_balance")
            if max_balance:
                try:
                    data["max_balance"] = int(max_balance)
                except ValueError:
                    data["max_balance"] = None
            if record:
                for field, value in data.items():
                    setattr(record, field, value)
            else:
                # creating new record
                record = Bin(bin=bin_code, **data)
                db.session.add(record)
            db.session.commit()
            message = "Record saved"
        elif action == "delete":
            record = Bin.query.filter_by(bin=bin_code).first()
            if record:
                db.session.delete(record)
                db.session.commit()
                message = f"Deleted BIN {bin_code}"
                record = None
            else:
                message = "BIN not found"
    return render_template(
        "admin_dashboard.html", message=message, record=record, colors=colors
    )


@admin_bp.route("/submissions")
@login_required
def submissions():
    colors = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    submissions = Submission.query.all()
    return render_template("admin_submissions.html", submissions=submissions, colors=colors)


@admin_bp.route("/submissions/<int:sub_id>", methods=["GET", "POST"])
@login_required
def view_submission(sub_id: int):
    colors = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    submission = Submission.query.get_or_404(sub_id)
    message: Optional[str] = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update":
            record = Bin.query.filter_by(bin=submission.bin).first()
            if not record:
                record = Bin(bin=submission.bin)
                db.session.add(record)
            fields = [
                "category",
                "reloadable",
                "international",
                "max_balance",
                "company",
                "country",
                "customer_service",
                "distributor",
                "issuer",
                "type",
                "website_url",
            ]
            for field in fields:
                value = request.form.get(field) or None
                if field == "max_balance" and value:
                    try:
                        value = int(value)
                    except ValueError:
                        value = None
                setattr(record, field, value)
            db.session.delete(submission)
            db.session.commit()
            message = "BIN updated"
        elif action == "delete":
            db.session.delete(submission)
            db.session.commit()
            return redirect(url_for("admin.submissions"))
    return render_template(
        "admin_submission_detail.html", submission=submission, message=message, colors=colors
    )
