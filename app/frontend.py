"""Frontend blueprint for BIN lookup homepage."""

from __future__ import annotations

from flask import Blueprint, render_template, request, current_app, abort, url_for, redirect

from . import db

from .models import Bin, Submission

frontend_bp = Blueprint("frontend", __name__)


@frontend_bp.route("/", methods=["GET", "POST"])
def index():
    """Display search form and optionally BIN information."""
    bin_info = None
    error = None
    searched_bin = None
    if request.method == "POST":
        bin_code = request.form.get("bin", "").strip()
        if not bin_code.isdigit() or len(bin_code) != 6:
            error = "Please enter a valid 6 digit BIN."
        else:
            record = Bin.query.filter_by(bin=bin_code).first()
            if record:
                bin_info = record.as_dict()
                # Replace None values with a friendly message
                for key, value in bin_info.items():
                    if value is None or value == "":
                        bin_info[key] = "Not Available"
                # Hide prepaid-specific fields when not a prepaid card
                if bin_info.get("category", "").lower() != "prepaid":
                    for field in ["reloadable", "international", "max_balance", "company"]:
                        bin_info.pop(field, None)
            else:
                error = "BIN not found."
        searched_bin = bin_code
    cfg = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    colors = {
        "primary_color": cfg.get("primary_color", "#007BFF"),
        "secondary_color": cfg.get("secondary_color", "#0056b3"),
    }
    site_name = cfg.get("site_name", "BIN Lookup")
    logo = cfg.get("logo", {})
    description = cfg.get("description", "")
    disclaimer_enabled = cfg.get("disclaimer_enabled", False)

    return render_template(
        "index.html",
        bin_info=bin_info,
        error=error,
        colors=colors,
        site_name=site_name,
        logo=logo,
        description=description,
        disclaimer_enabled=disclaimer_enabled,
        searched_bin=searched_bin,
    )


@frontend_bp.route("/report/<bin_code>", methods=["GET", "POST"])
def report(bin_code: str):
    """Allow users to submit corrections for a BIN."""
    if not bin_code.isdigit() or len(bin_code) != 6:
        abort(404)

    record = Bin.query.filter_by(bin=bin_code).first()
    bin_info = record.as_dict() if record else {}

    message = None
    if request.method == "POST":
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
        if data.get("max_balance"):
            try:
                data["max_balance"] = int(data["max_balance"])
            except ValueError:
                data["max_balance"] = None
        submission = Submission(bin=bin_code, **data)
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for("frontend.report", bin_code=bin_code, message="1"))

    message_flag = request.args.get("message")
    if message_flag:
        message = "Thank you for your submission."

    cfg = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    colors = {
        "primary_color": cfg.get("primary_color", "#007BFF"),
        "secondary_color": cfg.get("secondary_color", "#0056b3"),
    }
    return render_template(
        "report.html", bin_code=bin_code, colors=colors, message=message, bin_info=bin_info
    )


@frontend_bp.route("/api-docs")
def api_docs():
    """Render API documentation for public endpoints."""
    cfg = current_app.config.get("APP_CONFIG", {}).get("frontend", {})
    colors = {
        "primary_color": cfg.get("primary_color", "#007BFF"),
        "secondary_color": cfg.get("secondary_color", "#0056b3"),
    }
    site_name = cfg.get("site_name", "BIN Lookup")
    domain = current_app.config.get("APP_CONFIG", {}).get("custom_domain")
    if not domain:
        domain = request.host_url.rstrip("/")
    return render_template(
        "api_docs.html", colors=colors, site_name=site_name, domain=domain
    )


