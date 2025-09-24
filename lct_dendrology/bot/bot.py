from __future__ import annotations

from typing import Final

from telegram import Update
from telegram.ext import (
    AIORateLimiter,
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


STUB_TEXT: Final[str] = "Заглушка: изображение получено. Текст будет здесь."


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "Привет! Отправь мне изображение, а я верну текст-заглушку."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None:
        return
    # Photo sizes are sorted by file size, last is the biggest
    if not update.effective_message.photo:
        return
    # We do not actually need to download the image for the stub reply.
    await update.effective_message.reply_text(STUB_TEXT)


def create_application(token: str) -> Application:
    """Create and configure the Telegram Application instance."""
    application = (
        ApplicationBuilder()
        .token(token)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    return application


async def run_polling(application: Application) -> None:
    """Start the bot using long polling."""
    await application.initialize()
    await application.start()
    try:
        await application.updater.start_polling()
        # Keep running until termination
        await application.updater.wait_for_stop()
    finally:
        await application.stop()
        await application.shutdown()


