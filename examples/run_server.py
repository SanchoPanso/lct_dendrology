#!/usr/bin/env python3
"""Script to run the FastAPI server."""

import uvicorn
import os
from pathlib import Path

from lct_dendrology.backend.server import app


def main() -> None:
    """Run the FastAPI server."""
    # Получаем настройки из переменных окружения
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("SERVER_RELOAD", "true").lower() == "true"
    
    print(f"Запуск сервера на http://{host}:{port}")
    print("Документация API доступна по адресу: http://localhost:8000/docs")
    print("Альтернативная документация: http://localhost:8000/redoc")
    
    # Запускаем сервер
    uvicorn.run(
        "lct_dendrology.backend.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()
