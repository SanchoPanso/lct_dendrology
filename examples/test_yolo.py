#!/usr/bin/env python3
"""Тестовый скрипт для проверки работы YOLO модели."""

import sys
import logging
from pathlib import Path

# Добавляем путь к пакету
sys.path.insert(0, str(Path(__file__).parent.parent))

from lct_dendrology.backend.server import (
    process_image_with_yolo,
    read_image_from_bytes,
    run_yolo_inference,
    extract_detections_from_results
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_individual_functions():
    """Тестирует каждую функцию отдельно."""
    try:
        import numpy as np
        from PIL import Image
        import io
        
        logger.info("=== Тестирование отдельных функций ===")
        
        # Создаем тестовое изображение
        image_array = np.ones((640, 640, 3), dtype=np.uint8) * 255
        pil_image = Image.fromarray(image_array)
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        image_bytes = img_byte_arr.getvalue()
        
        logger.info("✅ Тестовое изображение создано")
        
        # Тест 1: Чтение изображения
        logger.info("1. Тестирование read_image_from_bytes...")
        read_image = read_image_from_bytes(image_bytes)
        logger.info(f"✅ Изображение прочитано, форма: {read_image.shape}")
        
        # Тест 2: Инференс YOLO
        logger.info("2. Тестирование run_yolo_inference...")
        results = run_yolo_inference(read_image)
        logger.info(f"✅ Инференс завершен, получено {len(results)} результатов")
        
        # Тест 3: Извлечение детекций
        logger.info("3. Тестирование extract_detections_from_results...")
        detections = extract_detections_from_results(results)
        logger.info(f"✅ Извлечено {len(detections)} детекций")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании отдельных функций: {str(e)}")
        return False


def test_complete_pipeline():
    """Тестирует полный пайплайн обработки."""
    try:
        import numpy as np
        from PIL import Image
        import io
        
        logger.info("=== Тестирование полного пайплайна ===")
        
        # Создаем тестовое изображение
        image_array = np.ones((640, 640, 3), dtype=np.uint8) * 255
        pil_image = Image.fromarray(image_array)
        
        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        image_bytes = img_byte_arr.getvalue()
        
        logger.info("✅ Тестовое изображение создано")
        
        # Тестируем полный пайплайн
        detections = process_image_with_yolo(image_bytes)
        
        logger.info(f"✅ Полный пайплайн завершен, найдено {len(detections)} объектов")
        
        for i, detection in enumerate(detections):
            logger.info(f"Объект {i+1}: {detection}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании полного пайплайна: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("Запуск тестирования YOLO модели...")
    
    # Тестируем отдельные функции
    individual_success = test_individual_functions()
    
    # Тестируем полный пайплайн
    pipeline_success = test_complete_pipeline()
    
    if individual_success and pipeline_success:
        logger.info("✅ Все тесты прошли успешно!")
    else:
        logger.error("❌ Некоторые тесты завершились с ошибкой!")
        sys.exit(1)
