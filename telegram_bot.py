# telegram_bot.py

from __future__ import annotations

import asyncio
from typing import List, Tuple

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from app import create_app, db
from app.models import Bin

# Create Flask app for database access
flask_app = create_app()
with flask_app.app_context():
    db.create_all()
    config = flask_app.config.get("APP_CONFIG", {})

_application: Application | None = None
_loop: asyncio.AbstractEventLoop | None = None


def build_message(record: Bin) -> str:
    """Build a multi-line message for a BIN record."""
    lines: List[str] = [f"BIN: {record.bin}"]
    mapping: List[Tuple[str, str | None]] = [
        ("Category", record.category),
        ("Reloadable", record.reloadable),
        ("International", record.international),
    ]
    if record.max_balance is not None:
        mapping.append(("Max Balance", f"${record.max_balance}"))
    mapping.extend(
        [
            ("Company", record.company),
            ("Country", record.country),
            ("Customer Service", record.customer_service),
            ("Distributor", record.distributor),
            ("Issuer", record.issuer),
            ("Type", record.type),
            ("Website", record.website_url),
        ]
    )
    for key, value in mapping:
        if value:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information."""
    await update.message.reply_text("Use /lookup <BIN> to get BIN details.")


async def lookup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lookup a BIN and reply with its information."""
    if not context.args:
        await update.message.reply_text("Please provide a BIN, e.g. /lookup 123456")
        return

    bin_code = context.args[0].strip()
    if not bin_code.isdigit() or len(bin_code) != 6:
        await update.message.reply_text("Please provide a valid 6 digit BIN.")
        return

    with flask_app.app_context():
        record = Bin.query.filter_by(bin=bin_code).first()

    if not record:
        await update.message.reply_text("BIN not found.")
        return

    message = build_message(record)
    await update.message.reply_text(message)


def run_bot() -> None:
    """
    Entry point used by other modules.
    Creates a fresh event loop so it doesn’t conflict with Flask’s loop.
    """
    global _application, _loop

    tg_cfg = config.get("telegram", {})
    if not tg_cfg.get("enabled"):
        print("Telegram bot disabled in config.json")
        return

    token = tg_cfg.get("bot_token")
    if not token:
        print("Telegram bot token not configured")
        return

    # Build the Application (async) but do NOT call asyncio.run()
    _application = ApplicationBuilder().token(token).build()
    _application.add_handler(CommandHandler("start", start_command))
    _application.add_handler(CommandHandler("lookup", lookup_command))

    commands = [
        BotCommand("start", "Show help message"),
        BotCommand("lookup", "Lookup a BIN"),
    ]

    # Set commands synchronously in its own loop
    # Create a fresh event loop for this bot:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    # Since set_my_commands is async, run it on our new loop:
    _loop.run_until_complete(_application.bot.set_my_commands(commands))

    # Now run polling on that same loop:
    try:
        _loop.run_until_complete(_application.run_polling(stop_signals=None))
    finally:
        _application = None
        _loop.close()
        _loop = None


def stop_bot() -> None:
    """Stop the Telegram bot if it’s running."""
    if _application and _loop:
        # Stop and shutdown on the bot's loop
        fut1 = asyncio.run_coroutine_threadsafe(_application.stop(), _loop)
        fut2 = asyncio.run_coroutine_threadsafe(_application.shutdown(), _loop)
        fut1.result()
        fut2.result()


if __name__ == "__main__":
    run_bot()
