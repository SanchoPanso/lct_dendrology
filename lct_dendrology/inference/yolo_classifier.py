from typing import Any, Dict, List
import torch
from PIL import Image


class YoloClassifier:
    """
    Класс для классификации изображений с помощью YOLO классификатора.
    """
    def __init__(self, model_path: str = None, device: str = "cpu"):
        self.model_path = model_path or "yolo11n-cls.pt"
        self.device = device
        self.model = self._load_model()

    def _load_model(self):
        # Загрузка YOLO классификатора через torch hub или ultralytics
        try:
            from ultralytics import YOLO
            model = YOLO(self.model_path)
            model.to(self.device)
            return model
        except ImportError:
            raise RuntimeError("Для работы YoloClassifier требуется ultralytics>=8.0.0")

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Классифицирует изображение и возвращает результат.
        Args:
            image: PIL.Image.Image
        Returns:
            dict: Результаты классификации
        """
        results = self.model(image)
        # results[0].probs содержит вероятности классов
        probs = results[0].probs
        class_id = int(probs.top1)
        class_name = self.model.names[class_id]
        confidence = float(probs.top1conf)
        return {
            "class_id": class_id,
            "class_name": class_name,
            "confidence": confidence,
            "all_probs": probs.cpu().tolist()
        }
