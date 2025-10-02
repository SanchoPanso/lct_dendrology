#!/bin/bash
TARGET_DIR="$(dirname "$0")/../models"

mkdir -p "$TARGET_DIR"
wget -O "$TARGET_DIR/species_classifier_v2.pt" "https://github.com/SanchoPanso/lct_dendrology/releases/download/v0.3.0/species_classifier_v2.pt"
wget -O "$TARGET_DIR/tree_detector_v2.pt" "https://github.com/SanchoPanso/lct_dendrology/releases/download/v0.3.0/tree_detector_v2.pt"
