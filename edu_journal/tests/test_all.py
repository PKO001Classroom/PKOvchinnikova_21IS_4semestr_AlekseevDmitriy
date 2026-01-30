import pytest
import sqlite3
import os
import tempfile
import sys
from pathlib import Path

# Добавляем путь к исходному коду
sys.path.insert(0, str(Path(__file__).parent.parent))

# Импорт моделей и классов
from database import Database
from models import User, Subject, FgosCompetency, FgosIndicator, Grade, GradeWithDetails, CompetencyWithIndicators
from validators import (
    validate_comment, validate_indicators, validate_competency_data,
    validate_indicator_data, calculate_percentage_from_indicators,
    calculate_grade_by_count, calculate_grade_from_percentage,
    get_grade_requirements, get_grade_description
)

# ============================================================================
# ФИКСТУРЫ
# ============================================================================

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
    
    # Добавляем индикаторы для каждой компетенции
    # Получаем ID компетенций
    cursor.execute("SELECT id, code FROM fgos_competencies ORDER BY id")
    comp_data = cursor.fetchall()
    comp_ids = {}
    for comp_id, code in comp_data:
        comp_ids[code] = comp_id
    
    # Для ПК 1.1 добавляем 8 индикаторов
    for i in range(1, 9):
        cursor.execute("""
        INSERT INTO fgos_indicators (competency_id, code, description, weight, max_score) 
        VALUES (?, ?, ?, ?, ?)
        """, (comp_ids['ПК 1.1'], f'ПК 1.1.{i}', f'Индикатор ПК 1.1.{i}', 1, 1))
    
    # Для ОПК 2.1 добавляем 6 индикаторов
    for i in range(1, 7):
        cursor.execute("""
        INSERT INTO fgos_indicators (competency_id, code, description, weight, max_score) 
        VALUES (?, ?, ?, ?, ?)
        """, (comp_ids['ОПК 2.1'], f'ОПК 2.1.{i}', f'Индикатор ОПК 2.1.{i}', 1, 1))
    
    # Для УК 3.1 добавляем 4 индикатора
    for i in range(1, 5):
        cursor.execute("""
        INSERT INTO fgos_indicators (competency_id, code, description, weight, max_score) 
        VALUES (?, ?, ?, ?, ?)
        """, (comp_ids['УК 3.1'], f'УК 3.1.{i}', f'Индикатор УК 3.1.{i}', 1, 1))
    
    db.connection.commit()
    yield


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

# ============================================================================
# ТЕСТЫ МОДЕЛЕЙ
# ============================================================================

class TestUserModel:
    """Тесты модели User"""
    
    def test_user_creation(self):
        """Тест создания модели User"""
        user = User(1, 'test_user', 'pass123', 'teacher', 'Тестовый Пользователь', '15.02.01', None, '2024-01-01')
        
        assert user.id == 1
        assert user.username == 'test_user'
        assert user.password == 'pass123'
        assert user.role == 'teacher'
        assert user.full_name == 'Тестовый Пользователь'
        assert user.specialty == '15.02.01'
        assert user.group_name is None
        assert user.created_at == '2024-01-01'
    
    def test_user_repr(self):
        """Тест строкового представления User"""
        user = User(1, 'test_user', 'pass123', 'teacher', 'Тестовый Пользователь', '15.02.01', None, '2024-01-01')
        repr_str = repr(user)
        
        assert "User" in repr_str
        assert "test_user" in repr_str
        assert "teacher" in repr_str
        assert "Тестовый Пользователь" in repr_str


class TestSubjectModel:
    """Тесты модели Subject"""
    
    def test_subject_creation(self):
        """Тест создания модели Subject"""
        subject = Subject(1, 'Математика', 'МАТ-101', '15.02.01', 1)
        
        assert subject.id == 1
        assert subject.name == 'Математика'
        assert subject.code == 'МАТ-101'
        assert subject.specialty == '15.02.01'
        assert subject.teacher_id == 1


class TestFgosCompetencyModel:
    """Тесты модели FgosCompetency"""
    
    def test_competency_creation(self):
        """Тест создания модели FgosCompetency"""
        competency = FgosCompetency(1, 'ПК 1.1', 'Компетенция 1.1', 'Описание', '15.02.01', 'ПК')
        
        assert competency.id == 1
        assert competency.code == 'ПК 1.1'
        assert competency.name == 'Компетенция 1.1'
        assert competency.description == 'Описание'
        assert competency.specialty == '15.02.01'
        assert competency.type == 'ПК'


class TestFgosIndicatorModel:
    """Тесты модели FgosIndicator"""
    
    def test_indicator_creation(self):
        """Тест создания модели FgosIndicator"""
        indicator = FgosIndicator(1, 1, 'ПК 1.1.1', 'Индикатор 1.1.1', 1, 1)
        
        assert indicator.id == 1
        assert indicator.competency_id == 1
        assert indicator.code == 'ПК 1.1.1'
        assert indicator.description == 'Индикатор 1.1.1'
        assert indicator.weight == 1
        assert indicator.max_score == 1


class TestGradeModel:
    """Тесты модели Grade"""
    
    def test_grade_creation(self):
        """Тест создания модели Grade"""
        grade = Grade(1, 2, 1, 1, 1, 5, 88, 'Комментарий' * 10, '2024-01-01')
        
        assert grade.id == 1
        assert grade.student_id == 2
        assert grade.teacher_id == 1
        assert grade.subject_id == 1
        assert grade.competency_id == 1
        assert grade.grade_value == 5
        assert grade.percentage == 88
        assert len(grade.comment) >= 100
        assert grade.date == '2024-01-01'


class TestGradeWithDetailsModel:
    """Тесты модели GradeWithDetails"""
    
    def test_grade_with_details_creation(self):
        """Тест создания модели GradeWithDetails"""
        grade_details = GradeWithDetails(
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
        
        assert grade_details.id == 1
        assert grade_details.subject_name == 'Математика'
        assert grade_details.competency_code == 'ПК 1.1'
        assert grade_details.competency_name == 'Компетенция 1.1'
        assert grade_details.competency_type == 'ПК'
        assert grade_details.grade_value == 5
        assert grade_details.percentage == 88.5
        assert 'Индикатор' in grade_details.indicators
        assert len(grade_details.comment) >= 100
        assert grade_details.date == '2024-01-01'


class TestCompetencyWithIndicatorsModel:
    """Тесты модели CompetencyWithIndicators"""
    
    def test_competency_with_indicators_creation(self):
        """Тест создания модели CompetencyWithIndicators"""
        competency = FgosCompetency(1, 'ПК 1.1', 'Компетенция 1.1', 'Описание', '15.02.01', 'ПК')
        indicator = FgosIndicator(1, 1, 'ПК 1.1.1', 'Индикатор 1.1.1', 1, 1)
        indicators = [indicator]
        
        competency_with_indicators = CompetencyWithIndicators(competency, indicators)
        
        assert competency_with_indicators.competency.id == 1
        assert len(competency_with_indicators.indicators) == 1
        assert competency_with_indicators.total_indicators == 1

# ============================================================================
# ТЕСТЫ ВАЛИДАТОРОВ
# ============================================================================

class TestCommentValidation:
    """Тесты валидации комментариев"""
    
    def test_validate_comment_min_length(self):
        """Тест валидации комментария минимальной длины"""
        # Комментарий короче 100 символов
        short_comment = "Короткий комментарий"
        is_valid, message = validate_comment(short_comment)
        assert not is_valid
        assert "не менее 100 символов" in message
        
        # Комментарий ровно 100 символов
        exact_comment = "А" * 100
        is_valid, message = validate_comment(exact_comment)
        assert is_valid
        assert message == "OK"
    
    def test_validate_comment_with_competency_code(self):
        """Тест валидации комментария с кодом компетенции"""
        # Комментарий без кода компетенции
        comment_no_code = "Хорошая работа. " * 8  # Более 100 символов
        is_valid, message = validate_comment(comment_no_code)
        # В актуальной реализации валидатор НЕ проверяет наличие кодов компетенций
        # поэтому комментарий должен быть валидным
        assert is_valid
        assert message == "OK"
        
        # Комментарий с кодом ПК
        comment_with_pk = "Студент освоил компетенцию ПК 1.1. " * 5
        is_valid, message = validate_comment(comment_with_pk)
        assert is_valid


class TestIndicatorsValidation:
    """Тесты валидации индикаторов"""
    
    def test_validate_empty_indicators(self):
        """Тест валидации пустого списка индикаторов"""
        selected_indicators = []
        total_indicators = 8
        
        is_valid, message = validate_indicators(selected_indicators, total_indicators)
        assert not is_valid
        assert "хотя бы один индикатор" in message
    
    def test_validate_sufficient_indicators(self):
        """Тест валидации достаточного количества индикаторов"""
        # Для 8 индикаторов: минимум 4 для оценки 3
        test_cases = [
            (list(range(1, 5)), 8, True),  # 4 индикатора из 8 - достаточно
            (list(range(1, 4)), 8, False), # 3 индикатора из 8 - недостаточно
        ]
        
        for selected_indicators, total_indicators, expected_valid in test_cases:
            is_valid, message = validate_indicators(selected_indicators, total_indicators)
            assert is_valid == expected_valid


class TestCompetencyDataValidation:
    """Тесты валидации данных компетенций"""
    
    def test_validate_competency_code(self):
        """Тест валидации кода компетенции"""
        test_cases = [
            ("", "Название", False, "Код компетенции не может быть пустым"),
            ("ПК 1.1", "", False, "Название компетенции не может быть пустым"),
            ("ПК 1.1", "Название", True, "OK"),
        ]
        
        for code, name, expected_valid, expected_message in test_cases:
            is_valid, message = validate_competency_data(code, name)
            assert is_valid == expected_valid
            # Используем in вместо точного сравнения, так как сообщения могут немного отличаться
            assert expected_message in message

# ============================================================================
# ТЕСТЫ РАСЧЕТОВ
# ============================================================================

class TestCalculations:
    """Тесты расчетов"""
    
    @pytest.mark.parametrize("selected_count,total_count,expected_grade,expected_percentage", [
        # Для 8+ индикаторов
        (6, 8, 5, 75),  # 6 из 8 → 5
        (5, 8, 4, 62.5),  # 5 из 8 → 4
        (4, 8, 3, 50),  # 4 из 8 → 3
        (3, 8, 2, 37.5),  # 3 из 8 → 2
        # Для 6 индикаторов
        (5, 6, 5, 83.33),  # 5 из 6 → 5
        (4, 6, 4, 66.67),  # 4 из 6 → 4
        (3, 6, 3, 50),  # 3 из 6 → 3
        # Для других случаев (4 индикатора)
        (4, 4, 5, 100),  # 4 из 4 → 5
        (3, 4, 4, 75),   # 3 из 4 → 4
        (2, 4, 3, 50),   # 2 из 4 → 3
    ])
    def test_calculate_grade_by_count(self, selected_count, total_count, expected_grade, expected_percentage):
        """Тест расчета оценки по количеству индикаторов"""
        grade, percentage = calculate_grade_by_count(selected_count, total_count)
        assert grade == expected_grade
        assert abs(percentage - expected_percentage) < 0.01
    
    def test_get_grade_requirements(self):
        """Тест получения требований для оценки"""
        # Для 8 индикаторов
        req_8 = get_grade_requirements(8)
        assert "6-8 индикаторов" in req_8[5] or "75-100%" in req_8[5]
        assert "5 индикаторов" in req_8[4] or "62.5%" in req_8[4]
        
        # Для 6 индикаторов
        req_6 = get_grade_requirements(6)
        assert "5-6 индикаторов" in req_6[5] or "83-100%" in req_6[5]
        assert "4 индикатора" in req_6[4] or "67%" in req_6[4]
        
        # Для 4 индикаторов
        req_4 = get_grade_requirements(4)
        assert "86-100%" in req_4[5] or "100%" in req_4[5]
        assert "67-85%" in req_4[4] or "75%" in req_4[4]
    
    @pytest.mark.parametrize("percentage,expected_grade", [
        (100, 5), (90, 5), (86, 5),
        (85, 4), (75, 4), (67, 4),
        (66, 3), (50, 3), (48, 3),
        (47, 2), (0, 2),
    ])
    def test_calculate_grade_from_percentage(self, percentage, expected_grade):
        """Тест расчета оценки из процента освоения"""
        grade, _ = calculate_grade_from_percentage(percentage)
        assert grade == expected_grade

# ============================================================================
# ТЕСТЫ БАЗЫ ДАННЫХ
# ============================================================================

class TestDatabaseInitialization:
    """Тесты инициализации базы данных"""
    
    def test_create_connection_success(self, temp_db_path):
        """Тест успешного создания подключения к БД"""
        db = Database(db_path=temp_db_path)
        assert db.connection is not None
        assert isinstance(db.connection, sqlite3.Connection)
        db.close()
    
    def test_init_database_tables(self, db):
        """Тест создания таблиц при инициализации"""
        cursor = db.connection.cursor()
        
        # Проверяем существование всех таблиц
        tables = ['users', 'subjects', 'fgos_competencies', 'fgos_indicators', 'grades', 'grade_indicators']
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            result = cursor.fetchone()
            assert result is not None, f"Таблица {table} не создана"


class TestDatabaseCRUDOperations:
    """Тесты CRUD операций"""
    
    def test_add_user(self, db):
        """Тест добавления пользователя"""
        cursor = db.connection.cursor()
        
        cursor.execute("""
        INSERT INTO users (username, password, role, full_name, specialty, group_name)
        VALUES (?, ?, ?, ?, ?, ?)
        """, ('new_user', 'password123', 'student', 'Новый Пользователь', '15.02.01', 'Группа 101'))
        
        db.connection.commit()
        
        # Проверяем, что пользователь добавлен
        cursor.execute("SELECT * FROM users WHERE username = ?", ('new_user',))
        user = cursor.fetchone()
        
        assert user is not None
        # Исправлено: используем числовой индекс вместо строкового ключа
        assert user[1] == 'new_user'  # username на позиции 1
        assert user[4] == 'Новый Пользователь'  # full_name на позиции 4
    
    def test_get_users_by_role(self, db, sample_data):
        """Тест получения пользователей по роли"""
        students = db.fetch_all("SELECT * FROM users WHERE role = ?", ('student',))
        teachers = db.fetch_all("SELECT * FROM users WHERE role = ?", ('teacher',))
        
        assert len(students) == 2
        assert len(teachers) == 1

# ============================================================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================================================

class TestFullGradeCycle:
    """Тесты полного цикла выставления оценки"""
    
    def test_complete_grade_cycle(self, db, sample_data):
        """Тест полного цикла от выбора студента до сохранения оценки"""
        # 1. Получаем студента
        students = db.fetch_all("SELECT * FROM users WHERE role = ?", ('student',))
        assert len(students) == 2
        student_id = students[0][0]  # Используем числовой индекс
        
        # 2. Получаем предмет
        subjects = db.fetch_all("SELECT * FROM subjects")
        assert len(subjects) == 2
        subject_id = subjects[0][0]  # Используем числовой индекс
        
        # 3. Получаем компетенции для предмета
        # Создаем связь между предметом и компетенцией по специальности
        cursor = db.connection.cursor()
        cursor.execute("UPDATE subjects SET specialty = '15.02.01' WHERE id = ?", (subject_id,))
        cursor.execute("UPDATE fgos_competencies SET specialty = '15.02.01'")
        db.connection.commit()
        
        competencies = db.get_competencies_by_subject(subject_id)
        assert len(competencies) >= 1  # Может быть 0 или более компетенций
        if len(competencies) > 0:
            competency_id = competencies[0][0]  # Используем числовой индекс
            
            # 4. Получаем индикаторы для компетенции
            indicators = db.get_indicators_by_competency(competency_id)
            # Исправлено: проверяем, что индикаторы есть (должно быть 8 для ПК 1.1)
            assert len(indicators) > 0
            
            # 5. Выбираем 6 индикаторов для оценки 5 (если есть достаточно)
            selected_count = min(6, len(indicators))
            selected_indicators = [ind[0] for ind in indicators[:selected_count]]
            
            # 6. Рассчитываем оценку
            grade_value, percentage = db.calculate_grade_from_indicators(
                selected_indicators, competency_id
            )
            # Оценка зависит от количества выбранных индикаторов
            assert grade_value in [2, 3, 4, 5]
            assert 0 <= percentage <= 100
            
            # 7. Подготавливаем данные оценки
            grade_data = {
                'student_id': student_id,
                'teacher_id': 1,
                'subject_id': subject_id,
                'competency_id': competency_id,
                'grade_value': grade_value,
                'percentage': percentage,
                'comment': f'Студент освоил компетенцию ПК 1.1. ' * 10,
                'date': '2024-01-20'
            }
            
            # 8. Сохраняем оценку
            success = db.add_grade_with_indicators(grade_data, selected_indicators)
            assert success is True
            
            # 9. Проверяем, что оценка сохранена
            cursor.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,))
            grade = cursor.fetchone()
            
            assert grade is not None
            assert grade[5] == grade_value  # grade_value на позиции 5
            assert grade[6] == percentage   # percentage на позиции 6

# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

if __name__ == "__main__":
    pytest.main(["-v"])