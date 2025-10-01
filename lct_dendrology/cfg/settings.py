"""
Настройки проекта для дендрологических исследований.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Основные настройки проекта."""
    
    # Настройки Telegram Bot
    telegram_bot_token: str = Field(..., description="Токен Telegram бота")
    telegram_webhook_url: Optional[str] = Field(None, description="URL для webhook Telegram бота")
    telegram_webhook_port: int = Field(8443, description="Порт для webhook")
    send_excel_result: bool = Field(True, description="Выдавать пользователю файл Excel с результатами анализа")
    
    # Настройки FastAPI Backend
    backend_host: str = Field("0.0.0.0", description="Хост для FastAPI сервера")
    backend_port: int = Field(8000, description="Порт для FastAPI сервера")
    backend_workers: int = Field(1, description="Количество воркеров FastAPI")
    backend_reload: bool = Field(False, description="Автоперезагрузка FastAPI в режиме разработки")
    
    # Настройки модели
    model_path: Optional[str] = Field("models/tree_detector_v1.pt", description="Путь к файлу модели YOLO")
    model_device: str = Field("cpu", description="Устройство для инференса (cpu/cuda/mps)")
    model_batch_size: int = Field(1, description="Размер батча для инференса")
    model_confidence_threshold: float = Field(0.25, description="Порог уверенности для детекции (0.0-1.0)")
    model_iou_threshold: float = Field(0.45, description="Порог IoU для NMS (0.0-1.0)")
    model_enable_inference: bool = Field(True, description="Включить инференс модели (по умолчанию False - заглушка)")

    # Настройки классификатора деревьев
    classifier_model_path: str = Field("yolo11n-cls.pt", description="Путь к модели классификатора деревьев")
    classifier_confidence_threshold: float = Field(0.5, description="Порог уверенности для классификации породы дерева")
    
    # Настройки логирования
    log_level: str = Field("INFO", description="Уровень логирования")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Формат логов"
    )
    
    # Настройки данных
    data_dir: str = Field("./data", description="Директория с данными")
    images_dir: str = Field("./data/images", description="Директория с изображениями")
    results_dir: str = Field("./data/results", description="Директория с результатами")
    
    # Настройки безопасности
    secret_key: Optional[str] = Field(None, description="Секретный ключ для подписи")
    allowed_origins: list[str] = Field(["*"], description="Разрешенные источники для CORS")
    
    # Настройки базы данных (если потребуется)
    database_url: Optional[str] = Field(None, description="URL подключения к базе данных")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Глобальный экземпляр настроек
settings = Settings()
