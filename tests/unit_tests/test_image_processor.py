"""Юнит-тесты для ImageProcessor класса."""

import pytest
from unittest.mock import Mock, patch
from PIL import Image
import io

from lct_dendrology.backend.image_processor import ImageProcessor


class TestImageProcessor:
    @pytest.fixture
    def mock_yolo_detector(self):
        mock_detector = Mock()
        mock_detector.predict.return_value = {
            'detections': [
                {
                    'id': 0,
                    'class_id': 0,
                    'class_name': 'tree',
                    'confidence': 0.8,
                    'bbox': {'x1': 10, 'y1': 10, 'x2': 50, 'y2': 50},
                }
            ],
            'model_info': {'model_path': 'yolo11n.pt'}
        }
        mock_detector.get_model_info.return_value = {'model_path': 'yolo11n.pt'}
        return mock_detector

    @pytest.fixture
    def mock_yolo_classifier(self):
        mock_classifier = Mock()
        mock_classifier.predict.return_value = {
            'class_id': 1,
            'class_name': 'oak',
            'confidence': 0.9,
        }
        return mock_classifier

    @pytest.fixture
    def test_image_bytes(self):
        image = Image.new('RGB', (100, 100), 'red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()

    def test_process_image_inference_disabled(self, test_image_bytes):
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = False
            processor = ImageProcessor()
            result = processor.process_image(test_image_bytes)
            assert result['inference_enabled'] is False
            assert result['detections'] == []
            assert result['model_info']['status'] == 'disabled'

    def test_process_image_inference_enabled_with_classification(self, test_image_bytes, mock_yolo_detector, mock_yolo_classifier):
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings, \
             patch('lct_dendrology.backend.image_processor.YoloDetector', return_value=mock_yolo_detector), \
             patch('lct_dendrology.backend.image_processor.YoloClassifier', return_value=mock_yolo_classifier):
            mock_settings.model_enable_inference = True
            mock_settings.classifier_confidence_threshold = 0.5
            processor = ImageProcessor()
            result = processor.process_image(test_image_bytes)
            assert result['inference_enabled'] is True
            assert len(result['detections']) == 1
            det = result['detections'][0]
            assert det['species'] == 'oak'
            assert det['species_confidence'] == 0.9

    def test_process_image_inference_enabled_low_confidence(self, test_image_bytes, mock_yolo_detector, mock_yolo_classifier):
        mock_yolo_classifier.predict.return_value = {
            'class_id': 1,
            'class_name': 'oak',
            'confidence': 0.6,
        }
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings, \
             patch('lct_dendrology.backend.image_processor.YoloDetector', return_value=mock_yolo_detector), \
             patch('lct_dendrology.backend.image_processor.YoloClassifier', return_value=mock_yolo_classifier):
            mock_settings.model_enable_inference = True
            mock_settings.classifier_confidence_threshold = 0.7
            processor = ImageProcessor()
            result = processor.process_image(test_image_bytes)
            det = result['detections'][0]
            assert det['species'] is None
            assert det['species_confidence'] == 0.6

    def test_get_detector_info(self, mock_yolo_detector, mock_yolo_classifier):
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings, \
             patch('lct_dendrology.backend.image_processor.YoloDetector', return_value=mock_yolo_detector), \
             patch('lct_dendrology.backend.image_processor.YoloClassifier', return_value=mock_yolo_classifier):
            mock_settings.model_enable_inference = True
            processor = ImageProcessor()
            info = processor.get_detector_info()
            assert 'detector_info' in info
            assert 'classifier_info' in info
