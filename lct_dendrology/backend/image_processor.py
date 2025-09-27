"""
Модуль для обработки изображений с помощью YOLO модели.
"""

import logging
from typing import Dict, Any, Optional

from lct_dendrology.inference import YoloDetector
from lct_dendrology.cfg import settings

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Класс для обработки изображений с помощью YOLO модели."""
    
    def __init__(self):
        """Инициализация процессора изображений."""
        self._detector: Optional[YoloDetector] = None
        self._initialize_detector()
    
    def _initialize_detector(self) -> None:
        """Инициализирует YOLO детектор если инференс включен."""
        if settings.model_enable_inference:
            try:
                logger.info("Инициализация YOLO детектора...")
                self._detector = YoloDetector(
                    model_path=settings.model_path,
                    device=settings.model_device,
                    confidence_threshold=settings.model_confidence_threshold,
                    iou_threshold=settings.model_iou_threshold
                )
                logger.info("YOLO детектор успешно инициализирован")
            except Exception as e:
                logger.error(f"Ошибка при инициализации YOLO детектора: {str(e)}")
                self._detector = None
        else:
            logger.info("Инференс модели отключен в настройках")
    
    def process_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Обрабатывает изображение с помощью YOLO модели.
        
        Args:
            image_bytes: Байты изображения
            
        Returns:
            Dict с результатами обработки:
            {
                'detections': List[Dict] - список найденных объектов (если инференс включен),
                'model_info': Dict - информация о модели (если инференс включен),
                'inference_enabled': bool - флаг включения инференса
            }
        """
        result = {
            'inference_enabled': settings.model_enable_inference
        }
        
        if not settings.model_enable_inference:
            logger.info("Инференс отключен, возвращаем заглушку")
            result['detections'] = []
            result['model_info'] = {
                'status': 'disabled',
                'message': 'Инференс модели отключен в настройках'
            }
            return result
        
        if self._detector is None:
            logger.error("YOLO детектор не инициализирован")
            result['detections'] = []
            result['model_info'] = {
                'status': 'error',
                'message': 'YOLO детектор не инициализирован'
            }
            return result
        
        try:
            logger.info("Начинаем обработку изображения с помощью YOLO модели")
            
            # Выполняем предсказание
            detection_result = self._detector.predict(image_bytes)
            
            # Добавляем результаты детекции
            result['detections'] = detection_result['detections']
            result['model_info'] = detection_result['model_info']
            
            logger.info(f"Обработка завершена. Найдено объектов: {len(detection_result['detections'])}")
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при обработке изображения: {str(e)}")
            result['detections'] = []
            result['model_info'] = {
                'status': 'error',
                'message': f'Ошибка при обработке: {str(e)}'
            }
            return result
    
    def get_detector_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о детекторе.
        
        Returns:
            Dict с информацией о детекторе
        """
        if self._detector is None:
            return {
                'initialized': False,
                'inference_enabled': settings.model_enable_inference,
                'message': 'Детектор не инициализирован'
            }
        
        return {
            'initialized': True,
            'inference_enabled': settings.model_enable_inference,
            'detector_info': self._detector.get_model_info()
        }


# Глобальный экземпляр процессора изображений
image_processor = ImageProcessor()
