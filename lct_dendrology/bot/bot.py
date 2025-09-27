from __future__ import annotations

import asyncio
import logging
from typing import Final

import aiohttp
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

from lct_dendrology.cfg import settings


# Configure logging
logger = logging.getLogger(__name__)

# Configuration
STUB_TEXT: Final[str] = "Заглушка: изображение получено. Текст будет здесь."
SERVER_URL: Final[str] = f"http://{settings.backend_host}:{settings.backend_port}"
TIMEOUT: Final[int] = 30  # Можно добавить в настройки при необходимости


async def send_image_to_server(image_data: bytes, filename: str) -> dict:
    """
    Отправляет изображение на сервер для обработки.
    
    Args:
        image_data: Байты изображения
        filename: Имя файла
        
    Returns:
        Результат обработки от сервера
        
    Raises:
        Exception: При ошибке связи с сервером
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=TIMEOUT)) as session:
        data = aiohttp.FormData()
        data.add_field('file', image_data, filename=filename, content_type='image/jpeg')
        
        try:
            async with session.post(f"{SERVER_URL}/process-image", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Изображение успешно обработано сервером: {filename}")
                    return result
                else:
                    error_text = await response.text()
                    logger.error(f"Сервер вернул ошибку {response.status}: {error_text}")
                    raise Exception(f"Сервер вернул ошибку {response.status}")
                    
        except asyncio.TimeoutError:
            logger.error("Таймаут при обращении к серверу")
            raise Exception("Сервер не отвечает слишком долго")
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка связи с сервером: {str(e)}")
            raise Exception("Не удается подключиться к серверу")


def format_analysis_result(analysis: dict) -> str:
    """
    Форматирует результат анализа для вывода пользователю.
    Args:
        analysis: Словарь с результатом анализа
    Returns:
        Строка для отправки пользователю
    """
    detections = analysis.get('detections', [])
    if not detections:
        return (
            "📊 Результат анализа:\n\n"
            "Объекты не обнаружены на изображении."
        )
    # Считаем количество объектов каждого класса
    class_counts = {}
    for det in detections:
        name = det.get('class_name', 'unknown')
        class_counts[name] = class_counts.get(name, 0) + 1
    detected_list = "\n".join(
        [f"• {cls}: {count}" for cls, count in class_counts.items()]
    )
    return (
        "📊 Результат анализа:\n\n"
        "Найденные объекты:\n"
        f"{detected_list}\n\n"
        f"Всего объектов: {len(detections)}"
    )


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        "Привет! Отправь мне изображение, и я проанализирую его с помощью нейросети."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_message is None:
        return
    
    # Photo sizes are sorted by file size, last is the biggest
    if not update.effective_message.photo:
        return
    
    # Отправляем сообщение о том, что изображение получено
    processing_msg = await update.effective_message.reply_text(
        "🔄 Обрабатываю изображение..."
    )
    
    try:
        # Получаем самое большое изображение
        photo = update.effective_message.photo[-1]
        
        # Скачиваем файл
        file = await context.bot.get_file(photo.file_id)
        image_data = await file.download_as_bytearray()
        
        logger.info(f"Получено изображение размером {len(image_data)} байт")
        
        # Отправляем на сервер
        result = await send_image_to_server(
            bytes(image_data), 
            f"photo_{photo.file_id}.jpg"
        )
        
       # Формируем ответ пользователю
        analysis = result.get("analysis_result", {})
        if analysis.get('inference_enabled') is True:
            response_text = format_analysis_result(analysis)
        else:
            # Если результат пустой (заглушка), отправляем соответствующее сообщение
            response_text = (
                "✅ Изображение успешно получено!\n\n"
                "📋 Информация о файле:\n"
                f"• Размер: {result.get('file_size', 'неизвестно')} байт\n"
                f"• Тип: {result.get('content_type', 'неизвестно')}\n\n"
                "🤖 В данный момент нейросеть находится в режиме заглушки. "
                "Реальные результаты анализа появятся после интеграции модели."
            )
        
        # Обновляем сообщение с результатом
        await processing_msg.edit_text(response_text)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {str(e)}")
        
        # Отправляем сообщение об ошибке
        error_message = (
            "❌ Произошла ошибка при обработке изображения.\n\n"
            "Возможные причины:\n"
            "• Сервер временно недоступен\n"
            "• Проблемы с подключением к интернету\n"
            "• Неподдерживаемый формат изображения\n\n"
            "Попробуйте еще раз через несколько минут."
        )
        
        await processing_msg.edit_text(error_message)


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


