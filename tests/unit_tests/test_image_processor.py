"""Юнит-тесты для ImageProcessor класса."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import io

from lct_dendrology.backend.image_processor import ImageProcessor


class TestImageProcessor:
    """Тесты для ImageProcessor класса."""
    
    @pytest.fixture
    def mock_yolo_detector(self):
        """Создает мок YoloDetector."""
        mock_detector = Mock()
        mock_detector.predict.return_value = {
            'detections': [
                {
                    'id': 0,
                    'class_id': 0,
                    'class_name': 'person',
                    'confidence': 0.8,
                    'bbox': {'x1': 10, 'y1': 10, 'x2': 50, 'x2': 50},
                    'center': {'x': 30, 'y': 30},
                    'width': 40,
                    'height': 40,
                    'area': 1600
                }
            ],
            'model_info': {
                'model_path': 'yolo11n.pt',
                'device': 'cpu',
                'confidence_threshold': 0.25,
                'iou_threshold': 0.45
            }
        }
        mock_detector.get_model_info.return_value = {
            'model_path': 'yolo11n.pt',
            'device': 'cpu',
            'confidence_threshold': 0.25,
            'iou_threshold': 0.45,
            'model_loaded': True
        }
        return mock_detector
    
    @pytest.fixture
    def test_image_bytes(self):
        """Создает тестовые байты изображения."""
        image = Image.new('RGB', (100, 100), 'red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def test_init_with_inference_disabled(self):
        """Тест инициализации с отключенным инференсом."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = False
            
            processor = ImageProcessor()
            
            assert processor._detector is None
    
    def test_init_with_inference_enabled(self, mock_yolo_detector):
        """Тест инициализации с включенным инференсом."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings, \
             patch('lct_dendrology.backend.image_processor.YoloDetector', return_value=mock_yolo_detector):
            
            mock_settings.model_enable_inference = True
            mock_settings.model_path = 'test_model.pt'
            mock_settings.model_device = 'cpu'
            mock_settings.model_confidence_threshold = 0.5
            mock_settings.model_iou_threshold = 0.3
            
            processor = ImageProcessor()
            
            assert processor._detector is not None
    
    def test_init_with_inference_enabled_but_error(self):
        """Тест инициализации с включенным инференсом, но с ошибкой."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings, \
             patch('lct_dendrology.backend.image_processor.YoloDetector', side_effect=Exception("Model not found")):
            
            mock_settings.model_enable_inference = True
            
            processor = ImageProcessor()
            
            assert processor._detector is None
    
    def test_process_image_inference_disabled(self, test_image_bytes):
        """Тест обработки изображения с отключенным инференсом."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = False
            
            processor = ImageProcessor()
            result = processor.process_image(test_image_bytes)
            
            assert result['inference_enabled'] is False
            assert result['detections'] == []
            assert result['model_info']['status'] == 'disabled'
            assert 'Инференс модели отключен' in result['model_info']['message']
    
    def test_process_image_inference_enabled_success(self, test_image_bytes, mock_yolo_detector):
        """Тест успешной обработки изображения с включенным инференсом."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = True
            
            processor = ImageProcessor()
            processor._detector = mock_yolo_detector
            
            result = processor.process_image(test_image_bytes)
            
            assert result['inference_enabled'] is True
            assert len(result['detections']) == 1
            assert result['detections'][0]['class_name'] == 'person'
            assert 'model_info' in result
            mock_yolo_detector.predict.assert_called_once_with(test_image_bytes)
    
    def test_process_image_inference_enabled_but_detector_none(self, test_image_bytes):
        """Тест обработки изображения с включенным инференсом, но детектор не инициализирован."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = True
            
            processor = ImageProcessor()
            processor._detector = None
            
            result = processor.process_image(test_image_bytes)
            
            assert result['inference_enabled'] is True
            assert result['detections'] == []
            assert result['model_info']['status'] == 'error'
            assert 'не инициализирован' in result['model_info']['message']
    
    def test_process_image_inference_enabled_but_error(self, test_image_bytes, mock_yolo_detector):
        """Тест обработки изображения с включенным инференсом, но с ошибкой."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = True
            
            mock_yolo_detector.predict.side_effect = Exception("Processing error")
            
            processor = ImageProcessor()
            processor._detector = mock_yolo_detector
            
            result = processor.process_image(test_image_bytes)
            
            assert result['inference_enabled'] is True
            assert result['detections'] == []
            assert result['model_info']['status'] == 'error'
            assert 'Ошибка при обработке' in result['model_info']['message']
    
    def test_get_detector_info_detector_none(self):
        """Тест получения информации о детекторе, когда детектор не инициализирован."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = False
            
            processor = ImageProcessor()
            info = processor.get_detector_info()
            
            assert info['initialized'] is False
            assert info['inference_enabled'] is False
            assert 'не инициализирован' in info['message']
    
    def test_get_detector_info_detector_initialized(self, mock_yolo_detector):
        """Тест получения информации о детекторе, когда детектор инициализирован."""
        with patch('lct_dendrology.backend.image_processor.settings') as mock_settings:
            mock_settings.model_enable_inference = True
            
            processor = ImageProcessor()
            processor._detector = mock_yolo_detector
            
            info = processor.get_detector_info()
            
            assert info['initialized'] is True
            assert info['inference_enabled'] is True
            assert 'detector_info' in info
            assert info['detector_info']['model_loaded'] is True
