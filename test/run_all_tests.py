#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов
"""
import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Печать заголовка"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def run_command(command, description):
    """Запуск команды с выводом результата"""
    print(f"\n{description}...")
    print("-" * 40)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Успешно")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ Ошибка")
        if result.stderr:
            print(result.stderr)
    
    return result.returncode

def main():
    """Основная функция"""
    project_root = Path(__file__).parent
    
    print_header("Запуск тестов учебного журнала")
    
    # 1. Проверка установки зависимостей
    print("\n1. Проверка зависимостей...")
    try:
        import pytest
        import PyQt5
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Ошибка: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return 1
    
    # 2. Модульные тесты
    returncode = run_command(
        "python -m pytest tests/test_database.py tests/test_models.py tests/test_validators.py -v",
        "Модульные тесты"
    )
    
    if returncode != 0:
        print("\n❌ Модульные тесты провалены")
        return returncode
    
    # 3. Интеграционные тесты
    returncode = run_command(
        "python -m pytest tests/test_auth_integration.py tests/test_grade_flow.py -v",
        "Интеграционные тесты"
    )
    
    if returncode != 0:
        print("\n❌ Интеграционные тесты провалены")
        return returncode
    
    # 4. UI тесты
    returncode = run_command(
        "python -m pytest tests/test_login_window.py -v",
        "UI тесты"
    )
    
    if returncode != 0:
        print("\n❌ UI тесты провалены")
        return returncode
    
    # 5. Все тесты с отчетом
    print_header("Запуск всех тестов с отчетом")
    
    returncode = run_command(
        f"python -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing --cov-report=html:reports/coverage",
        "Все тесты с покрытием кода"
    )
    
    # 6. Итог
    print_header("Результаты тестирования")
    
    if returncode == 0:
        print("✅ Все тесты пройдены успешно!")
        print(f"\n📊 Отчет о покрытии сохранен в: {project_root}/reports/coverage/index.html")
    else:
        print("❌ Некоторые тесты провалены")
    
    return returncode

if __name__ == "__main__":
    sys.exit(main())