"""Flask application entry point."""

from __future__ import annotations

from app import create_app, db
from threading import Thread
from telegram_bot import run_bot, stop_bot

app = create_app()
with app.app_context():
    db.create_all()

cfg = app.config.get("APP_CONFIG", {})
bot_thread: Thread | None = None
if cfg.get("telegram", {}).get("enabled"):
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

if __name__ == "__main__":
    try:
        app.run("0.0.0.0")
    finally:
        if bot_thread:
            stop_bot()
            bot_thread.join()
