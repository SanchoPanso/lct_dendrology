import asyncio
import logging

from lct_dendrology.bot.bot import create_application
from lct_dendrology.cfg import settings


def main() -> None:
    """Запуск Telegram бота с использованием настроек из конфига."""
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Запуск Telegram бота...")
    logger.info(f"Уровень логирования: {settings.log_level}")
    
    # Проверяем наличие токена
    if not settings.telegram_bot_token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не установлен. "
            "Создайте файл .env или установите переменную окружения."
        )
    
    # Создаем приложение бота
    application = create_application(settings.telegram_bot_token)
    
    logger.info("Бот успешно инициализирован. Запуск polling...")
    
    # Запускаем бота
    application.run_polling(close_loop=False)


if __name__ == "__main__":
    main()



