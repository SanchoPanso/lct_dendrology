import os
import shutil
import random
from typing import List

def split_dataset(input_dir: str, output_dir: str, train_ratio: float = 0.8):
    os.makedirs(output_dir, exist_ok=True)
    train_dir = os.path.join(output_dir, "train")
    test_dir = os.path.join(output_dir, "test")
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_path):
            continue
        images = [f for f in os.listdir(class_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))]
        random.shuffle(images)
        split_idx = int(len(images) * train_ratio)
        train_images = images[:split_idx]
        test_images = images[split_idx:]

        train_class_dir = os.path.join(train_dir, class_name)
        test_class_dir = os.path.join(test_dir, class_name)
        os.makedirs(train_class_dir, exist_ok=True)
        os.makedirs(test_class_dir, exist_ok=True)

        for img in train_images:
            shutil.copy2(os.path.join(class_path, img), os.path.join(train_class_dir, img))
        for img in test_images:
            shutil.copy2(os.path.join(class_path, img), os.path.join(test_class_dir, img))
        print(f"{class_name}: train={len(train_images)}, test={len(test_images)}")

if __name__ == "__main__":

    input_dir = "data/crops_dryness"
    output_dir = "data/crops_dryness_splitted"
    train_ratio = 0.8
    split_dataset(input_dir, output_dir, train_ratio)
