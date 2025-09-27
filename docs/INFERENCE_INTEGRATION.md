# Интеграция инференса в бэкенд

## Обзор

В бэкенд была интегрирована возможность обработки изображений с помощью YOLO модели. Инференс может быть включен или отключен через настройки.

## Новые компоненты

### 1. Настройки

В `lct_dendrology/cfg/settings.py` добавлена новая настройка:

```python
model_enable_inference: bool = Field(False, description="Включить инференс модели (по умолчанию False - заглушка)")
```

### 2. ImageProcessor

Новый класс `ImageProcessor` в `lct_dendrology/backend/image_processor.py`:

- Управляет инициализацией YoloDetector
- Обрабатывает изображения с помощью модели
- Возвращает результаты детекции или заглушку в зависимости от настроек

### 3. Обновленный API

#### Endpoint `/process-image`
Теперь возвращает структурированный результат:

```json
{
  "filename": "image.jpg",
  "file_size": 825,
  "content_type": "image/jpeg",
  "analysis_result": {
    "inference_enabled": true,
    "detections": [
      {
        "id": 0,
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.8,
        "bbox": {"x1": 10, "y1": 10, "x2": 50, "y2": 50},
        "center": {"x": 30, "y": 30},
        "width": 40,
        "height": 40,
        "area": 1600
      }
    ],
    "model_info": {
      "model_path": "yolo11n.pt",
      "device": "cpu",
      "confidence_threshold": 0.25,
      "iou_threshold": 0.45
    }
  }
}
```

#### Новый endpoint `/processor-info`
Возвращает информацию о состоянии процессора изображений:

```json
{
  "initialized": true,
  "inference_enabled": true,
  "detector_info": {
    "model_path": "yolo11n.pt",
    "device": "cpu",
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45,
    "model_loaded": true
  }
}
```

## Использование

### Включение инференса

1. Через переменную окружения:
```bash
export MODEL_ENABLE_INFERENCE=true
```

2. Через файл `.env`:
```
MODEL_ENABLE_INFERENCE=true
```

### Отключение инференса

По умолчанию инференс отключен. При отключенном инференсе API возвращает заглушку:

```json
{
  "analysis_result": {
    "inference_enabled": false,
    "detections": [],
    "model_info": {
      "status": "disabled",
      "message": "Инференс модели отключен в настройках"
    }
  }
}
```

## Тестирование

Созданы комплексные тесты в `tests/unit_tests/test_image_processor.py`:

- Тесты инициализации с включенным/отключенным инференсом
- Тесты обработки изображений в различных сценариях
- Тесты обработки ошибок
- Тесты получения информации о процессоре

## Безопасность

- Инференс по умолчанию отключен
- Обработка ошибок на всех уровнях
- Логирование всех операций
- Graceful fallback при ошибках инициализации модели
