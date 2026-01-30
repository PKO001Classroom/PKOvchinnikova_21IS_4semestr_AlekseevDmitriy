import pytest
import sqlite3
import os
import tempfile
import sys
from pathlib import Path

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Database
from models import User, Subject, FgosCompetency, FgosIndicator, Grade, GradeWithDetails, CompetencyWithIndicators
import validators


@pytest.fixture
def temp_db_path():
    """Фикстура для создания временной базы данных"""
    # Создаем временный файл для базы данных
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield path
    
    # Очистка после тестов
    try:
        os.remove(path)
    except:
        pass


@pytest.fixture
def db(temp_db_path):
    """Фикстура для создания объекта базы данных"""
    # Создаем экземпляр Database с тестовым путем
    db_instance = Database(db_path=temp_db_path)
    
    # Инициализируем базу данных (создаем таблицы)
    conn = db_instance.create_connection()
    if conn:
        cursor = conn.cursor()
        
        # Создаем таблицы
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
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT,
            specialty TEXT,
            teacher_id INTEGER REFERENCES users(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fgos_competencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            specialty TEXT,
            type TEXT CHECK(type IN ('ПК', 'ОПК', 'УК'))
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fgos_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competency_id INTEGER NOT NULL,
            code TEXT NOT NULL,
            description TEXT NOT NULL,
            weight INTEGER DEFAULT 1,
            max_score INTEGER DEFAULT 1,
            FOREIGN KEY (competency_id) REFERENCES fgos_competencies(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            teacher_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            competency_id INTEGER NOT NULL,
            grade_value INTEGER NOT NULL CHECK(grade_value BETWEEN 2 AND 5),
            percentage INTEGER NOT NULL CHECK(percentage BETWEEN 0 AND 100),
            comment TEXT NOT NULL CHECK(LENGTH(comment) >= 100),
            date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (teacher_id) REFERENCES users(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            FOREIGN KEY (competency_id) REFERENCES fgos_competencies(id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS grade_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade_id INTEGER NOT NULL,
            indicator_id INTEGER NOT NULL,
            score INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (grade_id) REFERENCES grades(id),
            FOREIGN KEY (indicator_id) REFERENCES fgos_indicators(id)
        )
        ''')
        
        conn.commit()
    
    yield db_instance
    
    # Закрываем соединение
    db_instance.close()


@pytest.fixture
def sample_data(db):
    """Фикстура для создания тестовых данных"""
    cursor = db.connection.cursor()
    
    # Очищаем таблицы
    cursor.execute("DELETE FROM grade_indicators")
    cursor.execute("DELETE FROM grades")
    cursor.execute("DELETE FROM fgos_indicators")
    cursor.execute("DELETE FROM fgos_competencies")
    cursor.execute("DELETE FROM subjects")
    cursor.execute("DELETE FROM users")
    
    # Добавляем тестовых пользователей
    cursor.execute("""
    INSERT INTO users (username, password, role, full_name, specialty, group_name) 
    VALUES 
        ('test_teacher', 'pass123', 'teacher', 'Иванов И.И.', '15.02.01', NULL),
        ('test_student1', 'pass123', 'student', 'Петров П.П.', '15.02.01', 'Группа 101'),
        ('test_student2', 'pass123', 'student', 'Сидоров С.С.', '15.02.01', 'Группа 101')
    """)
    
    # Добавляем предметы
    cursor.execute("""
    INSERT INTO subjects (name, code, specialty, teacher_id) 
    VALUES 
        ('Математика', 'МАТ-101', '15.02.01', 1),
        ('Программирование', 'ПРОГ-102', '15.02.01', 1)
    """)
    
    # Добавляем компетенции
    cursor.execute("""
    INSERT INTO fgos_competencies (code, name, description, specialty, type) 
    VALUES 
        ('ПК 1.1', 'Компетенция 1.1', 'Описание ПК 1.1', '15.02.01', 'ПК'),
        ('ОПК 2.1', 'Компетенция 2.1', 'Описание ОПК 2.1', '15.02.01', 'ОПК'),
        ('УК 3.1', 'Компетенция 3.1', 'Описание УК 3.1', '15.02.01', 'УК')
    """)
    
    # Добавляем индикаторы для компетенций
    cursor.execute("""
    INSERT INTO fgos_indicators (competency_id, code, description, weight, max_score) 
    VALUES 
        (1, 'ПК 1.1.1', 'Индикатор 1.1.1', 1, 1),
        (1, 'ПК 1.1.2', 'Индикатор 1.1.2', 1, 1),
        (1, 'ПК 1.1.3', 'Индикатор 1.1.3', 2, 1),
        (1, 'ПК 1.1.4', 'Индикатор 1.1.4', 1, 1),
        (1, 'ПК 1.1.5', 'Индикатор 1.1.5', 1, 1),
        (1, 'ПК 1.1.6', 'Индикатор 1.1.6', 2, 1),
        (1, 'ПК 1.1.7', 'Индикатор 1.1.7', 1, 1),
        (1, 'ПК 1.1.8', 'Индикатор 1.1.8', 2, 1),
        (2, 'ОПК 2.1.1', 'Индикатор 2.1.1', 1, 1),
        (2, 'ОПК 2.1.2', 'Индикатор 2.1.2', 1, 1),
        (2, 'ОПК 2.1.3', 'Индикатор 2.1.3', 1, 1),
        (2, 'ОПК 2.1.4', 'Индикатор 2.1.4', 1, 1),
        (2, 'ОПК 2.1.5', 'Индикатор 2.1.5', 1, 1),
        (2, 'ОПК 2.1.6', 'Индикатор 2.1.6', 1, 1),
        (3, 'УК 3.1.1', 'Индикатор 3.1.1', 1, 1),
        (3, 'УК 3.1.2', 'Индикатор 3.1.2', 1, 1),
        (3, 'УК 3.1.3', 'Индикатор 3.1.3', 1, 1),
        (3, 'УК 3.1.4', 'Индикатор 3.1.4', 1, 1)
    """)
    
    db.connection.commit()
    yield
    
    # Очистка после теста
    cursor.execute("DELETE FROM grade_indicators")
    cursor.execute("DELETE FROM grades")
    db.connection.commit()

@pytest.fixture
def sample_data(init_test_db):
    """Фикстура для создания тестовых данных"""
    conn = init_test_db
    cursor = conn.cursor()
    
    # Очищаем таблицы
    cursor.execute("DELETE FROM grade_indicators")
    cursor.execute("DELETE FROM grades")
    cursor.execute("DELETE FROM fgos_indicators")
    cursor.execute("DELETE FROM fgos_competencies")
    cursor.execute("DELETE FROM subjects")
    cursor.execute("DELETE FROM users")
    
    # Добавляем тестовых пользователей
    cursor.execute("""
    INSERT INTO users (username, password, role, full_name, specialty, group_name) 
    VALUES 
        ('test_teacher', 'pass123', 'teacher', 'Иванов И.И.', '15.02.01', NULL),
        ('test_student1', 'pass123', 'student', 'Петров П.П.', '15.02.01', 'Группа 101'),
        ('test_student2', 'pass123', 'student', 'Сидоров С.С.', '15.02.01', 'Группа 101')
    """)
    
    # Добавляем предметы
    cursor.execute("""
    INSERT INTO subjects (name, code, specialty, teacher_id) 
    VALUES 
        ('Математика', 'МАТ-101', '15.02.01', 1),
        ('Программирование', 'ПРОГ-102', '15.02.01', 1)
    """)
    
    # Добавляем компетенции
    cursor.execute("""
    INSERT INTO fgos_competencies (code, name, description, specialty, type) 
    VALUES 
        ('ПК 1.1', 'Компетенция 1.1', 'Описание ПК 1.1', '15.02.01', 'ПК'),
        ('ОПК 2.1', 'Компетенция 2.1', 'Описание ОПК 2.1', '15.02.01', 'ОПК'),
        ('УК 3.1', 'Компетенция 3.1', 'Описание УК 3.1', '15.02.01', 'УК')
    """)
    
    # Добавляем индикаторы для компетенций
    cursor.execute("""
    INSERT INTO fgos_indicators (competency_id, code, description, weight, max_score) 
    VALUES 
        (1, 'ПК 1.1.1', 'Индикатор 1.1.1', 1, 1),
        (1, 'ПК 1.1.2', 'Индикатор 1.1.2', 1, 1),
        (1, 'ПК 1.1.3', 'Индикатор 1.1.3', 2, 1),
        (1, 'ПК 1.1.4', 'Индикатор 1.1.4', 1, 1),
        (1, 'ПК 1.1.5', 'Индикатор 1.1.5', 1, 1),
        (1, 'ПК 1.1.6', 'Индикатор 1.1.6', 2, 1),
        (1, 'ПК 1.1.7', 'Индикатор 1.1.7', 1, 1),
        (1, 'ПК 1.1.8', 'Индикатор 1.1.8', 2, 1),
        (2, 'ОПК 2.1.1', 'Индикатор 2.1.1', 1, 1),
        (2, 'ОПК 2.1.2', 'Индикатор 2.1.2', 1, 1),
        (2, 'ОПК 2.1.3', 'Индикатор 2.1.3', 1, 1),
        (2, 'ОПК 2.1.4', 'Индикатор 2.1.4', 1, 1),
        (2, 'ОПК 2.1.5', 'Индикатор 2.1.5', 1, 1),
        (2, 'ОПК 2.1.6', 'Индикатор 2.1.6', 1, 1),
        (3, 'УК 3.1.1', 'Индикатор 3.1.1', 1, 1),
        (3, 'УК 3.1.2', 'Индикатор 3.1.2', 1, 1),
        (3, 'УК 3.1.3', 'Индикатор 3.1.3', 1, 1),
        (3, 'УК 3.1.4', 'Индикатор 3.1.4', 1, 1)
    """)
    
    conn.commit()
    yield conn
    
    # Очистка после теста
    cursor.execute("DELETE FROM grade_indicators")
    cursor.execute("DELETE FROM grades")
    conn.commit()


@pytest.fixture
def sample_user():
    """Фикстура для создания тестового пользователя"""
    return User(1, 'test_user', 'pass123', 'teacher', 'Тестовый Пользователь', '15.02.01', None, '2024-01-01')


@pytest.fixture
def sample_subject():
    """Фикстура для создания тестового предмета"""
    return Subject(1, 'Математика', 'МАТ-101', '15.02.01', 1)


@pytest.fixture
def sample_competency():
    """Фикстура для создания тестовой компетенции"""
    return FgosCompetency(1, 'ПК 1.1', 'Компетенция 1.1', 'Описание', '15.02.01', 'ПК')


@pytest.fixture
def sample_indicator():
    """Фикстура для создания тестового индикатора"""
    return FgosIndicator(1, 1, 'ПК 1.1.1', 'Индикатор 1.1.1', 1, 1)


@pytest.fixture
def sample_grade():
    """Фикстура для создания тестовой оценки"""
    grade = Grade(1, 2, 1, 1, 1, 5, 88, 'Комментарий' * 10, '2024-01-01')
    grade.selected_indicators = [1, 2, 3]
    return grade


@pytest.fixture
def sample_grade_with_details():
    """Фикстура для создания тестовой оценки с деталями"""
    return GradeWithDetails(
        grade_id=1,
        subject_name='Математика',
        competency_code='ПК 1.1',
        competency_name='Компетенция 1.1',
        competency_type='ПК',
        grade_value=5,
        percentage=88.5,
        indicators='Индикатор 1; Индикатор 2',
        comment='Хорошая работа' * 10,
        date='2024-01-01',
        teacher_name='Иванов И.И.'
    )


@pytest.fixture
def sample_competency_with_indicators(sample_competency, sample_indicator):
    """Фикстура для создания компетенции с индикаторами"""
    indicators = [sample_indicator]
    return CompetencyWithIndicators(sample_competency, indicators)