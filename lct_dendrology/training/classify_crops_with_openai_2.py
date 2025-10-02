import os
import io
import requests
import base64
from io import BytesIO
from PIL import Image
import pandas as pd
from typing import List
from openai import OpenAI


# --- Конфигурация ---
IMAGES_DIR = "/mnt/c/Users/Alex/Downloads/Санитарка(3)/Санитарка/"
YOLO_LABELS_DIR = "runs/detect/predict2/labels"
OUTPUT_DIR = "./data/crops_dryness/"

client = OpenAI(base_url="http://10.0.71.50:8099/v1/", api_key="EMPTY")

os.makedirs(OUTPUT_DIR, exist_ok=True)


# --- Функции ---
def parse_yolo_label(label_path: str) -> List[dict]:
    """Парсит YOLO label файл и возвращает список bbox."""
    bboxes = []
    with open(label_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            class_id, x_center, y_center, w, h = map(float, parts)
            bboxes.append({
                "class_id": int(class_id),
                "x_center": x_center,
                "y_center": y_center,
                "w": w,
                "h": h
            })
    return bboxes


def yolo_to_bbox(yolo_bbox, img_w, img_h):
    """Преобразует YOLO bbox в координаты (x1, y1, x2, y2)."""
    x_c, y_c, w, h = yolo_bbox["x_center"], yolo_bbox["y_center"], yolo_bbox["w"], yolo_bbox["h"]
    x1 = int((x_c - w / 2) * img_w)
    y1 = int((y_c - h / 2) * img_h)
    x2 = int((x_c + w / 2) * img_w)
    y2 = int((y_c + h / 2) * img_h)
    return x1, y1, x2, y2


def classify_crop_with_openai(image_bytes: bytes) -> str:
    """Отправляет изображение в OpenAI VLM и возвращает класс."""
    img_str = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:image/png;base64,{img_str}"
    classes = [
        "сухое",
        "несухое",

    ]
    prompt = (
        "Определи класс сухости дерева на изображении. "
        "Выведи только один класс из списка: " + ", ".join(classes) + ". "
        "Если ни один класс не подходит, выведи 'unknown'."
    )
    resp = client.chat.completions.create(
        model="/model",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
    )
    result = resp.choices[0].message.content.strip().lower().replace(".", "")
    return result


from concurrent.futures import ThreadPoolExecutor, as_completed

def process_single_image(img_name):
    if not img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
        return
    img_path = os.path.join(IMAGES_DIR, img_name)
    label_path = os.path.join(YOLO_LABELS_DIR, os.path.splitext(img_name)[0] + ".txt")
    if not os.path.exists(label_path):
        print(f"Нет разметки для {img_name}")
        return
    img = Image.open(img_path).convert("RGB")
    img_w, img_h = img.size
    bboxes = parse_yolo_label(label_path)
    for i, bbox in enumerate(bboxes):
        x1, y1, x2, y2 = yolo_to_bbox(bbox, img_w, img_h)
        crop = img.crop((x1, y1, x2, y2))
        crop_bytes = io.BytesIO()
        crop.save(crop_bytes, format="JPEG")
        crop_bytes.seek(0)
        # Классификация через OpenAI VLM
        try:
            class_name = classify_crop_with_openai(crop_bytes.getvalue())
        except Exception as e:
            print(f"Ошибка классификации: {e}")
            class_name = "unknown"
        # Сохраняем вырез в папку по классу
        class_dir = os.path.join(OUTPUT_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)
        crop_filename = f"{os.path.splitext(img_name)[0]}_obj{i}.jpg"
        crop.save(os.path.join(class_dir, crop_filename))
        print(f"Сохранен {crop_filename} в {class_dir}")

def process_images(num_workers=8):
    img_names = [n for n in os.listdir(IMAGES_DIR) if n.lower().endswith(('.jpg', '.jpeg', '.png'))]
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_single_image, img_name) for img_name in img_names]
        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    process_images()
