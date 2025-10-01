import pytest
import torch
from unittest.mock import MagicMock, patch
from PIL import Image

from lct_dendrology.inference.yolo_classifier import YoloClassifier


@pytest.fixture
def dummy_image():
    return Image.new("RGB", (224, 224))


def make_mock_results():
    mock_probs = MagicMock()
    mock_probs.top1 = 2
    mock_probs.top1conf = 0.85
    mock_result = MagicMock()
    mock_result.probs = mock_probs
    return [mock_result]


@patch("lct_dendrology.inference.yolo_classifier.YoloClassifier._load_model")
def test_predict_returns_expected_dict(mock_load_model, dummy_image):
    # Создаем мок-модель
    mock_model = MagicMock()
    mock_model.names = {0: "oak", 1: "pine", 2: "birch"}
    mock_model.return_value = make_mock_results()
    # mock_load_model.return_value = mock_model

    classifier = YoloClassifier(model_path="mock.pt", device="cpu")
    # Явно подменяем model, чтобы вызов classifier.model(image) возвращал наш результат
    classifier.model = mock_model

    result = classifier.predict(dummy_image)

    assert result["class_id"] == 2
    assert result["class_name"] == "birch"
    assert result["confidence"] == 0.85

pytest.main([__file__])
