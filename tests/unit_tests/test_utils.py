"""Утилиты для юнит-тестов."""

import io
from typing import Tuple
from PIL import Image


def create_test_image(width: int = 100, height: int = 100, format: str = "JPEG") -> Tuple[bytes, str]:
    """
    Создает тестовое изображение в памяти.
    
    Args:
        width: Ширина изображения
        height: Высота изображения
        format: Формат изображения (JPEG, PNG)
        
    Returns:
        Tuple[bytes, str]: Байты изображения и имя файла
    """
    # Создаем простое тестовое изображение
    image = Image.new('RGB', (width, height), color='red')
    
    # Сохраняем в байты
    img_buffer = io.BytesIO()
    image.save(img_buffer, format=format)
    img_bytes = img_buffer.getvalue()
    
    # Формируем имя файла
    filename = f"test_image.{format.lower()}"
    
    return img_bytes, filename


def create_test_image_file(width: int = 100, height: int = 100, format: str = "JPEG") -> io.BytesIO:
    """
    Создает файл-объект с тестовым изображением.
    
    Args:
        width: Ширина изображения
        height: Высота изображения
        format: Формат изображения (JPEG, PNG)
        
    Returns:
        io.BytesIO: Файл-объект с изображением
    """
    img_bytes, _ = create_test_image(width, height, format)
    return io.BytesIO(img_bytes)
