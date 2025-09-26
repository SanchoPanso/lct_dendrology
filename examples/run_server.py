#!/usr/bin/env python3
"""Script to run the FastAPI server."""

import uvicorn
import logging

from lct_dendrology.backend.server import app
from lct_dendrology.cfg import settings


def main() -> None:
    """Запуск FastAPI сервера с использованием настроек из конфига."""
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Запуск FastAPI сервера...")
    logger.info(f"Хост: {settings.backend_host}")
    logger.info(f"Порт: {settings.backend_port}")
    logger.info(f"Автоперезагрузка: {settings.backend_reload}")
    logger.info(f"Количество воркеров: {settings.backend_workers}")
    
    print(f"Запуск сервера на http://{settings.backend_host}:{settings.backend_port}")
    print("Документация API доступна по адресу: http://localhost:8000/docs")
    print("Альтернативная документация: http://localhost:8000/redoc")
    
    # Запускаем сервер
    uvicorn.run(
        "lct_dendrology.backend.server:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.backend_reload,
        workers=settings.backend_workers if not settings.backend_reload else 1,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
