import os
import pytest
import httpx

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets")
IMAGE_PATH = os.path.abspath(os.path.join(ASSETS_DIR, "bus.jpg"))
SERVER_URL = "http://localhost:8000/process-image"


@pytest.mark.asyncio
async def test_fastapi_image_inference():
    # Проверяем, что файл существует
    assert os.path.exists(IMAGE_PATH), f"Файл {IMAGE_PATH} не найден"
    # Открываем изображение
    with open(IMAGE_PATH, "rb") as f:
        image_bytes = f.read()
    # Отправляем запрос на сервер
    async with httpx.AsyncClient(timeout=30) as client:
        files = {"file": ("bus.jpg", image_bytes, "image/jpeg")}
        response = await client.post(SERVER_URL, files=files)
    assert response.status_code == 200, f"Статус ответа: {response.status_code}"
    result = response.json()
    # Проверяем, что результат содержит ключи анализа
    assert "analysis_result" in result, "Нет ключа 'analysis_result' в ответе сервера"
    analysis = result["analysis_result"]
    assert analysis.get("inference_enabled") is True, "inference_enabled должен быть True"
    detections = analysis.get("detections", [])
    assert isinstance(detections, list), "detections должен быть списком"
    # Проверяем, что хотя бы один объект найден
    assert len(detections) > 0, "Объекты не обнаружены на изображении"
