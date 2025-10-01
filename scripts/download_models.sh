#!/bin/bash
set -e
MODEL_URL="https://github.com/SanchoPanso/lct_dendrology/releases/download/v0.1.0/tree_detector_v1.pt"
TARGET_DIR="$(dirname "$0")/../models"
TARGET_PATH="$TARGET_DIR/tree_detector_v1.pt"

mkdir -p "$TARGET_DIR"
echo "Скачивание модели из $MODEL_URL ..."
wget -O "$TARGET_PATH" "$MODEL_URL"
echo "Модель сохранена в $TARGET_PATH"
