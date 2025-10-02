"""
Класс для инференса YOLO модели в дендрологических исследованиях.
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import numpy as np
from PIL import Image
import io

from ultralytics import YOLO
from lct_dendrology.cfg import settings

logger = logging.getLogger(__name__)


class YoloDetector:
    """
    Класс для работы с YOLO моделью для детекции объектов на изображениях.
    
    Поддерживает различные форматы входных данных и возвращает структурированные
    результаты детекции в виде списка словарей.
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        device: Optional[str] = None,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45
    ):
        """
        Инициализация YOLO модели.
        
        Args:
            model_path: Путь к файлу модели. По умолчанию используется yolo11n.pt
            device: Устройство для инференса (cpu, cuda, mps). По умолчанию из настроек
            confidence_threshold: Порог уверенности для детекции (0.0-1.0)
            iou_threshold: Порог IoU для NMS (0.0-1.0)
        """
        self.model_path = model_path or "yolo11n.pt"
        self.device = device or "cpu"
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        
        # Инициализация модели
        self._model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Загружает YOLO модель."""
        try:
            logger.info(f"Загрузка YOLO модели: {self.model_path}")
            self._model = YOLO(self.model_path)
            logger.info(f"Модель успешно загружена на устройство: {self.device}")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели {self.model_path}: {str(e)}")
            raise RuntimeError(f"Не удалось загрузить модель: {str(e)}")
    
    def predict(
        self, 
        image: Union[str, Path, np.ndarray, Image.Image, bytes],
        return_image: bool = False
    ) -> Dict[str, Any]:
        """
        Выполняет предсказание на изображении.
        
        Args:
            image: Входное изображение в различных форматах:
                - str/Path: путь к файлу изображения
                - np.ndarray: массив numpy с изображением
                - PIL.Image: объект PIL Image
                - bytes: байты изображения
            return_image: Возвращать ли изображение с нарисованными bounding box
            
        Returns:
            Dict с результатами детекции:
            {
                'detections': List[Dict] - список найденных объектов,
                'image_with_boxes': PIL.Image - изображение с bounding box (если return_image=True),
                'model_info': Dict - информация о модели
            }
        """
        try:
            # Подготавливаем изображение
            processed_image = self._prepare_image(image)
            
            # Выполняем предсказание
            results = self._model(
                processed_image,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                device=self.device
            )
            
            # Обрабатываем результаты
            detections = self._process_results(results[0])
            
            result = {
                'detections': detections,
                'model_info': {
                    'model_path': self.model_path,
                    'device': self.device,
                    'confidence_threshold': self.confidence_threshold,
                    'iou_threshold': self.iou_threshold
                }
            }
            
            # Добавляем изображение с bounding box если требуется
            if return_image:
                result['image_with_boxes'] = results[0].plot()
            
            logger.info(f"Найдено объектов: {len(detections)}")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при выполнении предсказания: {str(e)}")
            raise RuntimeError(f"Ошибка инференса: {str(e)}")
    
    def _prepare_image(self, image: Union[str, Path, np.ndarray, Image.Image, bytes]) -> Union[str, Path, np.ndarray]:
        """
        Подготавливает изображение для YOLO модели.
        
        Args:
            image: Входное изображение в различных форматах
            
        Returns:
            Изображение в формате, подходящем для YOLO
        """
        if isinstance(image, (str, Path)):
            # Путь к файлу - возвращаем как есть
            return str(image)
        elif isinstance(image, bytes):
            # Байты - конвертируем в PIL Image, затем в numpy
            pil_image = Image.open(io.BytesIO(image))
            return np.array(pil_image)
        elif isinstance(image, Image.Image):
            # PIL Image - конвертируем в numpy
            return np.array(image)
        elif isinstance(image, np.ndarray):
            # numpy array - возвращаем как есть
            return image
        else:
            raise ValueError(f"Неподдерживаемый тип изображения: {type(image)}")
    
    def _process_results(self, result) -> List[Dict[str, Any]]:
        """
        Обрабатывает результаты YOLO и возвращает структурированный список детекций.
        
        Args:
            result: Результат YOLO модели
            
        Returns:
            List[Dict] - список детекций с информацией об объектах
        """
        detections = []
        
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()  # координаты bbox
            confidences = result.boxes.conf.cpu().numpy()  # уверенность
            class_ids = result.boxes.cls.cpu().numpy()  # ID классов
            
            # Получаем имена классов
            class_names = result.names
            
            for i, (box, conf, class_id) in enumerate(zip(boxes, confidences, class_ids)):
                detection = {
                    'id': i + 1,
                    'class_id': int(class_id),
                    'class_name': class_names[int(class_id)],
                    'confidence': float(conf),
                    'bbox': {
                        'x1': float(box[0]),
                        'y1': float(box[1]),
                        'x2': float(box[2]),
                        'y2': float(box[3])
                    },
                    'center': {
                        'x': float((box[0] + box[2]) / 2),
                        'y': float((box[1] + box[3]) / 2)
                    },
                    'width': float(box[2] - box[0]),
                    'height': float(box[3] - box[1]),
                    'area': float((box[2] - box[0]) * (box[3] - box[1]))
                }
                detections.append(detection)
        
        return detections
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о загруженной модели.
        
        Returns:
            Dict с информацией о модели
        """
        if self._model is None:
            return {"error": "Модель не загружена"}
        
        return {
            "model_path": self.model_path,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "iou_threshold": self.iou_threshold,
            "model_loaded": True
        }
    
    def update_thresholds(self, confidence: Optional[float] = None, iou: Optional[float] = None) -> None:
        """
        Обновляет пороги для детекции.
        
        Args:
            confidence: Новый порог уверенности (0.0-1.0)
            iou: Новый порог IoU (0.0-1.0)
        """
        if confidence is not None:
            if 0.0 <= confidence <= 1.0:
                self.confidence_threshold = confidence
                logger.info(f"Порог уверенности обновлен: {confidence}")
            else:
                raise ValueError("Порог уверенности должен быть между 0.0 и 1.0")
        
        if iou is not None:
            if 0.0 <= iou <= 1.0:
                self.iou_threshold = iou
                logger.info(f"Порог IoU обновлен: {iou}")
            else:
                raise ValueError("Порог IoU должен быть между 0.0 и 1.0")

