"""Flask application setup and configuration loader."""

from __future__ import annotations

import json
from pathlib import Path
import secrets
from io import BytesIO
import urllib.request

try:  # Optional dependency
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover - Pillow may not be installed
    Image = None

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def load_config() -> dict:
    """Load configuration from ``config.json`` file."""
    config_path = Path(__file__).resolve().parents[1] / "config.json"
    with open(config_path, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def setup_favicon(app: Flask, config: dict) -> None:
    """Download and convert the logo image to ``favicon.ico`` if possible."""
    logo_cfg = config.get("frontend", {}).get("logo", {})
    if not (logo_cfg.get("enabled") and logo_cfg.get("image_url") and Image):
        return
    try:
        with urllib.request.urlopen(logo_cfg["image_url"]) as resp:
            data = resp.read()
        img = Image.open(BytesIO(data))
        img = img.convert("RGBA")
        ico_path = Path(app.root_path) / "static" / "favicon.ico"
        ico_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(ico_path, format="ICO", sizes=[(32, 32)])
    except Exception:
        # Fail silently if anything goes wrong
        pass


def create_app() -> Flask:
    """Create and configure a Flask application instance."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bins.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    config = load_config()
    app.config["APP_CONFIG"] = config
    app.config["API_KEY"] = config.get("api", {}).get("api_key", "")

    setup_favicon(app, config)

    if config.get("api", {}).get("enabled", False):
        from .api import api_bp

        app.register_blueprint(api_bp)

    from .frontend import frontend_bp
    app.register_blueprint(frontend_bp)

    if config.get("admin", {}).get("enabled", False):
        from .admin import admin_bp

        app.register_blueprint(admin_bp)

    # Placeholder for future blueprints (e.g. Telegram)
    return app
