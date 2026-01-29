import pytest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

@pytest.fixture(scope="session")
def qapp():
    """Фикстура QApplication для всех тестов"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def qtbot(qapp, request):
    """Фикстура QtBot для тестирования UI"""
    from pytestqt.qtbot import QtBot
    bot = QtBot(request)
    yield bot
    bot.stop()

@pytest.fixture
def temp_db_file():
    """Фикстура временного файла базы данных"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def mock_db():
    """Мок базы данных"""
    mock = MagicMock()
    
    # Настраиваем возвращаемые значения
    mock.check_user.return_value = (1, "test_user", "test_pass", "student", "Test User")
    mock.get_student_grades.return_value = [
        ("Математика", 5, "Отлично", "2024-01-15"),
        ("Программирование", 4, "Хорошо", "2024-01-16")
    ]
    mock.fetch_one.return_value = (4.5,)  # Средний балл
    mock.fetch_all.return_value = []  # Пустой список по умолчанию
    
    return mock

@pytest.fixture
def test_user_data():
    """Тестовые данные пользователя"""
    return {
        "id": 1,
        "username": "test_user",
        "password": "test_pass",
        "role": "student",
        "full_name": "Test User",
        "specialty": "15.02.01",
        "group_name": "Group 101"
    }

@pytest.fixture
def teacher_user_data():
    """Тестовые данные преподавателя"""
    return {
        "id": 2,
        "username": "teacher_test",
        "password": "teacher_pass",
        "role": "teacher",
        "full_name": "Test Teacher",
        "specialty": "15.02.01",
        "group_name": None
    }