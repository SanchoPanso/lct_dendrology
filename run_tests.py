#!/usr/bin/env python3
"""Скрипт для запуска тестов проекта."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Запускает все тесты проекта."""
    project_root = Path(__file__).parent
    
    print("🧪 Запуск тестов проекта LCT Dendrology...")
    print("=" * 50)
    
    # Запускаем юнит-тесты
    print("\n📋 Юнит-тесты:")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit_tests/", 
        "-v", 
        "--tb=short"
    ], cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ Все тесты прошли успешно!")
    else:
        print("\n❌ Некоторые тесты не прошли.")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
