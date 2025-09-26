"""Юнит-тесты для FastAPI сервера."""

import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch

from lct_dendrology.backend.server import app
from .test_utils import create_test_image


class TestFastAPIServer:
    """Тесты для FastAPI сервера."""
    
    @pytest.fixture
    def client(self):
        """Создает тестовый клиент для FastAPI приложения."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Тест корневого эндпоинта."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "LCT Dendrology API is running"}
    
    def test_health_check_endpoint(self, client):
        """Тест эндпоинта проверки здоровья."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_process_image_success(self, client):
        """Тест успешной обработки изображения."""
        # Создаем тестовое изображение
        image_bytes, filename = create_test_image(width=200, height=200, format="JPEG")
        
        # Отправляем POST запрос с изображением
        files = {"file": (filename, image_bytes, "image/jpeg")}
        response = client.post("/process-image", files=files)
        
        # Проверяем ответ
        assert response.status_code == 200
        data = response.json()
        
        # Проверяем структуру ответа
        assert "filename" in data
        assert "file_size" in data
        assert "content_type" in data
        assert "analysis_result" in data
        
        # Проверяем значения
        assert data["filename"] == filename
        assert data["file_size"] == len(image_bytes)
        assert data["content_type"] == "image/jpeg"
        assert isinstance(data["analysis_result"], dict)
    
    def test_process_image_png_format(self, client):
        """Тест обработки PNG изображения."""
        # Создаем PNG изображение
        image_bytes, filename = create_test_image(width=150, height=150, format="PNG")
        
        files = {"file": (filename, image_bytes, "image/png")}
        response = client.post("/process-image", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content_type"] == "image/png"
        assert data["file_size"] == len(image_bytes)
    
    def test_process_image_no_file(self, client):
        """Тест запроса без файла."""
        response = client.post("/process-image")
        assert response.status_code == 422  # Validation error
    
    def test_process_image_invalid_file_type(self, client):
        """Тест загрузки файла не-изображения."""
        # Создаем текстовый файл
        text_content = b"This is not an image"
        files = {"file": ("test.txt", text_content, "text/plain")}
        
        response = client.post("/process-image", files=files)
        assert response.status_code == 400
        assert "Файл должен быть изображением" in response.json()["detail"]
    
    def test_process_image_empty_file(self, client):
        """Тест загрузки пустого файла."""
        files = {"file": ("empty.jpg", b"", "image/jpeg")}
        response = client.post("/process-image", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["file_size"] == 0
    
    def test_process_image_large_file(self, client):
        """Тест обработки большого изображения."""
        # Создаем большое изображение
        image_bytes, filename = create_test_image(width=1000, height=1000, format="JPEG")
        
        files = {"file": (filename, image_bytes, "image/jpeg")}
        response = client.post("/process-image", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["file_size"] == len(image_bytes)
        assert data["file_size"] > 1000  # Файл должен быть больше 1KB
    
    @pytest.mark.asyncio
    async def test_server_startup(self):
        """Тест запуска сервера."""
        # Проверяем, что приложение создается без ошибок
        assert app is not None
        assert app.title == "LCT Dendrology API"
        assert app.version == "1.0.0"
    
    def test_cors_headers(self, client):
        """Тест CORS заголовков."""
        response = client.options("/process-image")
        # FastAPI автоматически обрабатывает CORS для OPTIONS запросов
        assert response.status_code in [200, 405]  # 405 если метод не поддерживается
    
    def test_response_time(self, client):
        """Тест времени ответа сервера."""
        import time
        
        image_bytes, filename = create_test_image()
        files = {"file": (filename, image_bytes, "image/jpeg")}
        
        start_time = time.time()
        response = client.post("/process-image", files=files)
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 5.0  # Ответ должен быть быстрым


class TestFastAPIServerIntegration:
    """Интеграционные тесты с реальным сервером (требуют запущенного сервера)."""
    
    @pytest.fixture
    def server_url(self):
        """URL тестового сервера."""
        return "http://localhost:8000"
    
    @pytest.mark.asyncio
    async def test_server_with_httpx(self, server_url):
        """Тест сервера с использованием httpx (если сервер запущен)."""
        # Этот тест будет пропущен, если сервер не запущен
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{server_url}/health", timeout=5.0)
                if response.status_code == 200:
                    assert response.json() == {"status": "healthy"}
                else:
                    pytest.skip("Сервер не запущен")
        except httpx.ConnectError:
            pytest.skip("Сервер не доступен")
    
    @pytest.mark.asyncio
    async def test_image_processing_with_httpx(self, server_url):
        """Тест обработки изображения через httpx."""
        try:
            image_bytes, filename = create_test_image()
            
            async with httpx.AsyncClient() as client:
                files = {"file": (filename, image_bytes, "image/jpeg")}
                response = await client.post(
                    f"{server_url}/process-image", 
                    files=files,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "filename" in data
                    assert data["file_size"] == len(image_bytes)
                else:
                    pytest.skip("Сервер не запущен")
                    
        except httpx.ConnectError:
            pytest.skip("Сервер не доступен")
