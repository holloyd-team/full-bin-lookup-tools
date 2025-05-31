"""RESTful API blueprint for BIN lookup operations."""

from __future__ import annotations

from typing import Any, Dict, List

from flask import Blueprint, Response, jsonify, request, current_app

from .models import Bin, Submission
from . import db


api_bp = Blueprint("api", __name__, url_prefix="/api")

# Endpoints that do not require authentication even when an API key is set
PUBLIC_ENDPOINTS = {"api.submit_report"}


@api_bp.before_request
def require_api_key() -> Response | None:
    """Authenticate requests or restrict methods based on API key config."""
    if request.endpoint in PUBLIC_ENDPOINTS:
        return None
    api_key: str = current_app.config.get("API_KEY", "")
    if api_key:
        header_key = request.headers.get("x-api-key")
        if header_key != api_key:
            return jsonify({"error": "Unauthorized"}), 401
        return None
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        return jsonify({"error": "Unauthorized"}), 401
    return None


@api_bp.get("/bin/<string:bin_code>")
def get_bin(bin_code: str) -> Response:
    """Retrieve a BIN record by its first six digits."""
    record = Bin.query.filter_by(bin=bin_code).first()
    if record:
        return jsonify(record.as_dict())
    return jsonify({"error": "BIN not found"}), 404


@api_bp.post("/bin")
def create_bin() -> Response:
    """Create a new BIN record."""
    data: Dict[str, Any] | None = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    required_fields = ["bin", "company", "country"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    if Bin.query.filter_by(bin=data["bin"]).first():
        return jsonify({"error": "BIN already exists"}), 400
    fields = [
        "bin",
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
    new_bin = Bin(**{field: data.get(field) for field in fields})
    db.session.add(new_bin)
    db.session.commit()
    return jsonify(new_bin.as_dict()), 201


@api_bp.put("/bin/<string:bin_code>")
def update_bin(bin_code: str) -> Response:
    """Update fields on an existing BIN record."""
    record = Bin.query.filter_by(bin=bin_code).first()
    if not record:
        return jsonify({"error": "BIN not found"}), 404
    data: Dict[str, Any] | None = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    updatable_fields = [
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
    for field in updatable_fields:
        if field in data:
            setattr(record, field, data[field])
    db.session.commit()
    return jsonify(record.as_dict())


@api_bp.delete("/bin/<string:bin_code>")
def delete_bin(bin_code: str) -> Response:
    """Delete a BIN record by its first six digits."""
    record = Bin.query.filter_by(bin=bin_code).first()
    if not record:
        return jsonify({"error": "BIN not found"}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": f"Deleted BIN {bin_code}"})


@api_bp.post("/report/<string:bin_code>")
def submit_report(bin_code: str) -> Response:
    """Accept user submissions for BIN corrections."""
    if not bin_code.isdigit() or len(bin_code) != 6:
        return jsonify({"error": "Invalid BIN"}), 400
    data: Dict[str, Any] | None = request.get_json()
    if data is None:
        data = {}
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
    values = {field: data.get(field) for field in fields}
    max_balance = values.get("max_balance")
    if max_balance is not None:
        try:
            values["max_balance"] = int(max_balance)
        except (TypeError, ValueError):
            values["max_balance"] = None
    submission = Submission(bin=bin_code, **values)
    db.session.add(submission)
    db.session.commit()
    return jsonify(submission.as_dict()), 201
