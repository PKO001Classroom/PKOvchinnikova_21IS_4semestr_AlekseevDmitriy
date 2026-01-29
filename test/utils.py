"""
Вспомогательные функции для тестов
"""
import tempfile
import sqlite3
from pathlib import Path

def create_test_database(db_path=None):
    """
    Создание тестовой базы данных
    
    Args:
        db_path: Путь к файлу БД (если None, создается временный файл)
    
    Returns:
        tuple: (путь к файлу БД, соединение с БД)
    """
    if db_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        db_path = temp_file.name
    
    conn = sqlite3.connect(db_path)
    
    # Создаем таблицы
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
        full_name TEXT NOT NULL,
        specialty TEXT,
        group_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблица предметов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT,
        specialty TEXT
    )
    ''')
    
    # Таблица оценок
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        grade_value INTEGER NOT NULL CHECK(grade_value BETWEEN 2 AND 5),
        comment TEXT NOT NULL,
        date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Добавляем тестовые данные
    cursor.executemany(
        "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
        [
            ("test_teacher", "pass", "teacher", "Test Teacher"),
            ("test_student", "pass", "student", "Test Student")
        ]
    )
    
    cursor.executemany(
        "INSERT INTO subjects (name, code, specialty) VALUES (?, ?, ?)",
        [
            ("Математика", "МАТ-101", "15.02.01"),
            ("Программирование", "ПРОГ-102", "15.02.01")
        ]
    )
    
    cursor.execute(
        "INSERT INTO grades (student_id, teacher_id, subject, grade_value, comment, date) VALUES (?, ?, ?, ?, ?, ?)",
        (2, 1, "Математика", 5, "Отлично! ПК 1.1", "2024-01-15")
    )
    
    conn.commit()
    
    return db_path, conn

def cleanup_test_database(db_path, conn):
    """
    Очистка тестовой базы данных
    
    Args:
        db_path: Путь к файлу БД
        conn: Соединение с БД
    """
    if conn:
        conn.close()
    
    if db_path and Path(db_path).exists():
        Path(db_path).unlink()

def compare_colors(color1, color2, tolerance=5):
    """
    Сравнение двух цветов с допуском
    
    Args:
        color1: Первый цвет (QColor или tuple)
        color2: Второй цвет (QColor или tuple)
        tolerance: Допуск по каждому компоненту
    
    Returns:
        bool: True если цвета похожи в пределах допуска
    """
    if hasattr(color1, 'getRgb'):
        r1, g1, b1, _ = color1.getRgb()
    else:
        r1, g1, b1 = color1
    
    if hasattr(color2, 'getRgb'):
        r2, g2, b2, _ = color2.getRgb()
    else:
        r2, g2, b2 = color2
    
    return (abs(r1 - r2) <= tolerance and
            abs(g1 - g2) <= tolerance and
            abs(b1 - b2) <= tolerance)