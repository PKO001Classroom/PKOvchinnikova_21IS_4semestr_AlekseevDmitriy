"""
Тестирование модуля database.py
"""
import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch

# Импортируем после добавления пути в conftest
from database import Database

class TestDatabase:
    """Тесты для класса Database"""
    
    @pytest.fixture(autouse=True)
    def setup(self, temp_db_file):
        """Настройка перед каждым тестом"""
        self.db_path = temp_db_file
        self.db = Database(self.db_path)
        yield
        self.db.close()
    
    def test_create_connection_success(self):
        """Тест успешного создания подключения"""
        conn = self.db.create_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
    
    def test_create_connection_failure(self):
        """Тест создания подключения к несуществующей директории"""
        with pytest.raises(Exception):
            Database("/non/existent/path/database.db")
    
    def test_init_database_creates_tables(self):
        """Тест создания таблиц при инициализации"""
        conn = self.db.create_connection()
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        assert 'users' in tables
        assert 'grades' in tables
        assert 'subjects' in tables
    
    def test_init_database_adds_test_data(self):
        """Тест добавления тестовых данных"""
        conn = self.db.create_connection()
        cursor = conn.cursor()
        
        # Проверяем наличие тестовых пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        assert user_count >= 2  # teacher1 и student1
        
        # Проверяем наличие тестовых предметов
        cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cursor.fetchone()[0]
        assert subject_count >= 3  # Математика, Программирование, Базы данных
        
        # Проверяем наличие тестовых оценок
        cursor.execute("SELECT COUNT(*) FROM grades")
        grade_count = cursor.fetchone()[0]
        assert grade_count >= 1
    
    def test_execute_query_insert(self):
        """Тест выполнения INSERT запроса"""
        query = """
        INSERT INTO users (username, password, role, full_name)
        VALUES (?, ?, ?, ?)
        """
        params = ("new_user", "new_pass", "student", "New User")
        
        cursor = self.db.execute_query(query, params)
        assert cursor is not None
        
        # Проверяем что пользователь добавлен
        cursor.execute("SELECT * FROM users WHERE username = ?", ("new_user",))
        user = cursor.fetchone()
        assert user is not None
        assert user[1] == "new_user"
    
    def test_execute_query_error(self):
        """Тест обработки ошибки SQL"""
        cursor = self.db.execute_query("INVALID SQL")
        assert cursor is None
    
    def test_fetch_all(self):
        """Тест получения всех результатов"""
        # Добавляем тестовые данные
        self.db.execute_query(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            ("fetch_user", "pass", "student", "Fetch User")
        )
        
        results = self.db.fetch_all("SELECT * FROM users WHERE username = ?", ("fetch_user",))
        assert len(results) == 1
        assert results[0][1] == "fetch_user"
    
    def test_fetch_one(self):
        """Тест получения одного результата"""
        result = self.db.fetch_one("SELECT COUNT(*) FROM users")
        assert result is not None
        assert isinstance(result[0], int)
    
    def test_check_user_valid_credentials(self):
        """Тест проверки правильных учетных данных"""
        # Сначала добавим пользователя
        self.db.execute_query(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            ("check_user", "check_pass", "teacher", "Check User")
        )
        
        user = self.db.check_user("check_user", "check_pass")
        assert user is not None
        assert user[1] == "check_user"
        assert user[2] == "check_pass"
        assert user[3] == "teacher"
    
    def test_check_user_invalid_credentials(self):
        """Тест проверки неправильных учетных данных"""
        user = self.db.check_user("nonexistent", "wrong")
        assert user is None
    
    def test_get_student_grades(self):
        """Тест получения оценок студента"""
        # Добавляем тестовые данные
        self.db.execute_query(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            ("grade_student", "pass", "student", "Grade Student")
        )
        
        self.db.execute_query(
            "INSERT INTO grades (student_id, teacher_id, subject, grade_value, comment, date) VALUES (?, ?, ?, ?, ?, ?)",
            (1, 1, "Тестирование", 5, "Отлично", "2024-01-20")
        )
        
        grades = self.db.get_student_grades("Grade Student")
        assert len(grades) > 0
        assert grades[0][0] == "Тестирование"
        assert grades[0][1] == 5
    
    def test_add_grade(self):
        """Тест добавления оценки"""
        result = self.db.add_grade("Test Student", "Test Subject", 4, "Test Comment", 1)
        assert result is True
        
        # Проверяем что оценка добавлена
        grades = self.db.fetch_all(
            "SELECT * FROM grades WHERE subject = ?",
            ("Test Subject",)
        )
        assert len(grades) == 1
        assert grades[0][3] == "Test Subject"
        assert grades[0][4] == 4
        assert grades[0][5] == "Test Comment"