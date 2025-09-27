import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from lct_dendrology.bot.bot import handle_photo, format_analysis_result

@pytest.mark.asyncio
async def test_handle_photo_inference_enabled(monkeypatch):
    # Мокаем update и context
    mock_update = MagicMock()
    mock_context = MagicMock()
    mock_message = AsyncMock()
    mock_update.effective_message = mock_message
    mock_message.photo = [MagicMock(), MagicMock()]
    mock_message.reply_text = AsyncMock(return_value=mock_message)
    mock_message.edit_text = AsyncMock()

    # Мокаем получение файла
    mock_file = MagicMock()
    mock_file.download_as_bytearray = AsyncMock(return_value=b"imagebytes")
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)

    # Мокаем серверный ответ с inference_enabled=True
    analysis_result = {
        "inference_enabled": True,
        "detections": [
            {"class_name": "tree"},
            {"class_name": "tree"},
            {"class_name": "bush"},
        ]
    }
    mock_result = {"analysis_result": analysis_result}
    monkeypatch.setattr("lct_dendrology.bot.bot.send_image_to_server", AsyncMock(return_value=mock_result))

    await handle_photo(mock_update, mock_context)

    # Проверяем, что edit_text вызван с форматированным результатом
    expected_text = format_analysis_result(analysis_result)
    mock_message.edit_text.assert_called_with(expected_text)

@pytest.mark.asyncio
async def test_handle_photo_stub(monkeypatch):
    # Мокаем update и context
    mock_update = MagicMock()
    mock_context = MagicMock()
    mock_message = MagicMock()
    mock_update.effective_message = mock_message
    mock_message.photo = [MagicMock(), MagicMock()]
    mock_message.reply_text = AsyncMock(return_value=mock_message)
    mock_message.edit_text = AsyncMock()

    # Мокаем получение файла
    mock_file = MagicMock()
    mock_file.download_as_bytearray = AsyncMock(return_value=b"imagebytes")
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)

    # Мокаем серверный ответ с inference_enabled=False
    mock_result = {
        "analysis_result": {"inference_enabled": False},
        "file_size": 12345,
        "content_type": "image/jpeg"
    }
    monkeypatch.setattr("lct_dendrology.bot.bot.send_image_to_server", AsyncMock(return_value=mock_result))

    await handle_photo(mock_update, mock_context)

    # Проверяем, что edit_text вызван с текстом-заглушкой
    assert "нейросеть находится в режиме заглушки" in mock_message.edit_text.call_args[0][0]


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__]))
