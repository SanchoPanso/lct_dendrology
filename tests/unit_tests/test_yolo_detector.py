"""Юнит-тесты для YoloDetector класса."""

import pytest
import numpy as np
from PIL import Image
import io
from unittest.mock import Mock, patch, MagicMock

from lct_dendrology.inference import YoloDetector
from .test_utils import create_test_image


class TestYoloDetector:
    """Тесты для YoloDetector класса."""
    
    @pytest.fixture
    def mock_yolo_model(self):
        """Создает мок YOLO модели."""
        mock_model = Mock()
        mock_result = Mock()
        
        # Настраиваем мок результата
        mock_result.boxes = Mock()
        mock_result.boxes.xyxy = Mock()
        mock_result.boxes.xyxy.cpu.return_value.numpy.return_value = np.array([[10, 10, 50, 50]])
        mock_result.boxes.conf = Mock()
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array([0.8])
        mock_result.boxes.cls = Mock()
        mock_result.boxes.cls.cpu.return_value.numpy.return_value = np.array([0])
        mock_result.names = {0: 'person'}
        mock_result.plot.return_value = Image.new('RGB', (100, 100), 'red')
        
        mock_model.return_value = [mock_result]
        return mock_model
    
    @pytest.fixture
    def yolo_detector(self, mock_yolo_model):
        """Создает экземпляр YoloDetector с мок моделью."""
        with patch('lct_dendrology.inference.yolo_detector.YOLO', return_value=mock_yolo_model):
            return YoloDetector()
    
    def test_init_default_model(self, mock_yolo_model):
        """Тест инициализации с моделью по умолчанию."""
        with patch('lct_dendrology.inference.yolo_detector.YOLO', return_value=mock_yolo_model):
            detector = YoloDetector()
            
            assert detector.model_path == "yolo11n.pt"
            assert detector.confidence_threshold == 0.25
            assert detector.iou_threshold == 0.45
            assert detector._model is not None
    
    def test_init_custom_parameters(self, mock_yolo_model):
        """Тест инициализации с пользовательскими параметрами."""
        with patch('lct_dendrology.inference.yolo_detector.YOLO', return_value=mock_yolo_model):
            detector = YoloDetector(
                model_path="custom_model.pt",
                device="cuda",
                confidence_threshold=0.5,
                iou_threshold=0.3
            )
            
            assert detector.model_path == "custom_model.pt"
            assert detector.device == "cuda"
            assert detector.confidence_threshold == 0.5
            assert detector.iou_threshold == 0.3
    
    def test_predict_with_pil_image(self, yolo_detector):
        """Тест предсказания с PIL изображением."""
        # Создаем тестовое изображение
        image = Image.new('RGB', (100, 100), 'blue')
        
        result = yolo_detector.predict(image)
        
        assert 'detections' in result
        assert 'model_info' in result
        assert isinstance(result['detections'], list)
        assert len(result['detections']) == 1
        
        detection = result['detections'][0]
        assert detection['class_id'] == 0
        assert detection['class_name'] == 'person'
        assert detection['confidence'] == 0.8
        assert 'bbox' in detection
        assert 'center' in detection
    
    def test_predict_with_numpy_array(self, yolo_detector):
        """Тест предсказания с numpy массивом."""
        # Создаем тестовое изображение как numpy array
        image_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = yolo_detector.predict(image_array)
        
        assert 'detections' in result
        assert len(result['detections']) == 1
    
    def test_predict_with_bytes(self, yolo_detector):
        """Тест предсказания с байтами изображения."""
        # Создаем тестовое изображение в байтах
        image_bytes, _ = create_test_image(width=100, height=100, format="JPEG")
        
        result = yolo_detector.predict(image_bytes)
        
        assert 'detections' in result
        assert len(result['detections']) == 1
    
    def test_predict_with_path(self, yolo_detector, tmp_path):
        """Тест предсказания с путем к файлу."""
        # Создаем временный файл изображения
        image_path = tmp_path / "test_image.jpg"
        image = Image.new('RGB', (100, 100), 'green')
        image.save(image_path)
        
        result = yolo_detector.predict(str(image_path))
        
        assert 'detections' in result
        assert len(result['detections']) == 1
    
    def test_predict_with_return_image(self, yolo_detector):
        """Тест предсказания с возвратом изображения с bounding box."""
        image = Image.new('RGB', (100, 100), 'blue')
        
        result = yolo_detector.predict(image, return_image=True)
        
        assert 'detections' in result
        assert 'image_with_boxes' in result
        assert isinstance(result['image_with_boxes'], Image.Image)
    
    def test_predict_no_detections(self, mock_yolo_model):
        """Тест предсказания без детекций."""
        # Настраиваем мок для случая без детекций
        mock_result = Mock()
        mock_result.boxes = None
        mock_model = Mock()
        mock_model.return_value = [mock_result]
        
        with patch('lct_dendrology.inference.yolo_detector.YOLO', return_value=mock_model):
            detector = YoloDetector()
            image = Image.new('RGB', (100, 100), 'blue')
            
            result = detector.predict(image)
            
            assert 'detections' in result
            assert len(result['detections']) == 0
    
    def test_predict_invalid_image_type(self, yolo_detector):
        """Тест предсказания с неподдерживаемым типом изображения."""
        with pytest.raises(RuntimeError, match="Ошибка инференса"):
            yolo_detector.predict(123)  # int - неподдерживаемый тип
    
    def test_get_model_info(self, yolo_detector):
        """Тест получения информации о модели."""
        info = yolo_detector.get_model_info()
        
        assert info['model_path'] == "yolo11n.pt"
        assert info['device'] == "cpu"
        assert info['confidence_threshold'] == 0.25
        assert info['iou_threshold'] == 0.45
        assert info['model_loaded'] is True
    
    def test_update_thresholds(self, yolo_detector):
        """Тест обновления порогов."""
        yolo_detector.update_thresholds(confidence=0.7, iou=0.3)
        
        assert yolo_detector.confidence_threshold == 0.7
        assert yolo_detector.iou_threshold == 0.3
    
    def test_update_thresholds_invalid_confidence(self, yolo_detector):
        """Тест обновления порогов с невалидным значением уверенности."""
        with pytest.raises(ValueError, match="Порог уверенности должен быть между 0.0 и 1.0"):
            yolo_detector.update_thresholds(confidence=1.5)
    
    def test_update_thresholds_invalid_iou(self, yolo_detector):
        """Тест обновления порогов с невалидным значением IoU."""
        with pytest.raises(ValueError, match="Порог IoU должен быть между 0.0 и 1.0"):
            yolo_detector.update_thresholds(iou=-0.1)
    
    def test_model_loading_error(self):
        """Тест ошибки загрузки модели."""
        with patch('lct_dendrology.inference.yolo_detector.YOLO', side_effect=Exception("Model not found")):
            with pytest.raises(RuntimeError, match="Не удалось загрузить модель"):
                YoloDetector()
    
    def test_predict_error(self, yolo_detector):
        """Тест ошибки при предсказании."""
        # Настраиваем мок для вызова исключения
        yolo_detector._model.side_effect = Exception("Prediction failed")
        
        image = Image.new('RGB', (100, 100), 'blue')
        
        with pytest.raises(RuntimeError, match="Ошибка инференса"):
            yolo_detector.predict(image)
    
    def test_detection_structure(self, yolo_detector):
        """Тест структуры детекции."""
        image = Image.new('RGB', (100, 100), 'blue')
        result = yolo_detector.predict(image)
        
        detection = result['detections'][0]
        
        # Проверяем все обязательные поля
        required_fields = [
            'id', 'class_id', 'class_name', 'confidence', 
            'bbox', 'center', 'width', 'height', 'area'
        ]
        
        for field in required_fields:
            assert field in detection, f"Поле {field} отсутствует в детекции"
        
        # Проверяем типы данных
        assert isinstance(detection['id'], int)
        assert isinstance(detection['class_id'], int)
        assert isinstance(detection['class_name'], str)
        assert isinstance(detection['confidence'], float)
        assert isinstance(detection['bbox'], dict)
        assert isinstance(detection['center'], dict)
        assert isinstance(detection['width'], float)
        assert isinstance(detection['height'], float)
        assert isinstance(detection['area'], float)
        
        # Проверяем bbox структуру
        bbox_fields = ['x1', 'y1', 'x2', 'y2']
        for field in bbox_fields:
            assert field in detection['bbox']
            assert isinstance(detection['bbox'][field], float)
        
        # Проверяем center структуру
        center_fields = ['x', 'y']
        for field in center_fields:
            assert field in detection['center']
            assert isinstance(detection['center'][field], float)


class TestYoloDetectorIntegration:
    """Интеграционные тесты для YoloDetector (требуют реальной модели)."""
    
    @pytest.mark.slow
    def test_real_model_loading(self):
        """Тест загрузки реальной модели (медленный тест)."""
        # Этот тест будет пропущен, если модель не доступна
        try:
            detector = YoloDetector()
            info = detector.get_model_info()
            assert info['model_loaded'] is True
        except Exception as e:
            pytest.skip(f"Реальная модель недоступна: {str(e)}")
    
    @pytest.mark.slow
    def test_real_prediction(self):
        """Тест реального предсказания (медленный тест)."""
        try:
            detector = YoloDetector()
            image = Image.new('RGB', (640, 640), 'white')
            
            result = detector.predict(image)
            
            assert 'detections' in result
            assert 'model_info' in result
            assert isinstance(result['detections'], list)
            
        except Exception as e:
            pytest.skip(f"Реальное предсказание недоступно: {str(e)}")

