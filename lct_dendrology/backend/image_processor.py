"""
Модуль для обработки изображений с помощью YOLO модели.
"""

import logging
from typing import Dict, Any, Optional

from lct_dendrology.inference import YoloDetector, YoloClassifier
from lct_dendrology.cfg import settings

logger = logging.getLogger(__name__)



class ImageProcessor:
    """Класс для обработки изображений: детекция и классификация деревьев."""
    def __init__(self):
        if settings.model_enable_inference:
            self.detector = YoloDetector(
                model_path=settings.tree_detector_model_path,
                device=settings.model_device,
                confidence_threshold=settings.tree_detector_confidence_threshold,
                iou_threshold=settings.tree_detector_iou_threshold
            )
            self.classifier = YoloClassifier(
                model_path=settings.classifier_model_path,
                device=settings.model_device
            )
        else:
            self.detector = None
            self.classifier = None
        self.class_confidence_threshold = settings.classifier_confidence_threshold

    def process_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Находит деревья на изображении и классифицирует их породу.
        Проверяет, что изображение валидное.
        Args:
            image_bytes: Байты изображения
        Returns:
            dict: результат анализа
        """
        from PIL import Image, UnidentifiedImageError
        import io
        result = {
            'inference_enabled': settings.model_enable_inference
        }
        # Проверка валидности изображения
        try:
            Image.open(io.BytesIO(image_bytes)).verify()
        except (UnidentifiedImageError, Exception):
            result['detections'] = []
            result['model_info'] = {
                'status': 'error',
                'message': 'Файл не может быть открыт как изображение'
            }
            return result

        if not settings.model_enable_inference:
            result['detections'] = []
            result['model_info'] = {
                'status': 'disabled',
                'message': 'Инференс модели отключен в настройках'
            }
            return result

        # Детектируем деревья
        detection_result = self.detector.predict(image_bytes)
        detections = detection_result.get('detections', [])
        classified_detections = []
        # Классифицируем каждое дерево
        for det in detections:
            # Вырезаем область дерева по bbox
            bbox = det.get('bbox')
            if bbox:
                img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                crop = img.crop((bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']))
                class_result = self.classifier.predict(crop)
                conf = class_result.get('confidence', 0)
                if conf >= self.class_confidence_threshold:
                    det['species'] = class_result.get('class_name')
                    det['species_confidence'] = conf
                else:
                    det['species'] = None
                    det['species_confidence'] = conf
            else:
                det['species'] = None
                det['species_confidence'] = None
            classified_detections.append(det)
        result['detections'] = classified_detections
        result['model_info'] = {
            'detector': detection_result.get('model_info'),
            'classifier': {
                'model_path': getattr(self.classifier, 'model_path', None),
                'confidence_threshold': self.class_confidence_threshold
            }
        }
        return result

    def get_detector_info(self) -> Dict[str, Any]:
        detector_info = None if self.detector is None else self.detector.get_model_info()
        classifier_info = {
            'model_path': None if self.classifier is None else getattr(self.classifier, 'model_path', None),
            'confidence_threshold': self.class_confidence_threshold
        }
        return {
            'detector_info': detector_info,
            'classifier_info': classifier_info,
        }


# Глобальный экземпляр процессора изображений
image_processor = ImageProcessor()
