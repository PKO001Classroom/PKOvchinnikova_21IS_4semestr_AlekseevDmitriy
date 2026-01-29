"""
Тестирование модуля models.py
"""
import pytest
from datetime import datetime
from models import User, Subject, Grade

class TestUserModel:
    """Тесты для модели User"""
    
    def test_user_creation_with_all_fields(self):
        """Тест создания пользователя со всеми полями"""
        user = User(
            user_id=1,
            username="test_user",
            password="test_pass",
            role="teacher",
            full_name="Test User",
            specialty="15.02.01",
            group_name="Группа 101"
        )
        
        assert user.id == 1
        assert user.username == "test_user"
        assert user.password == "test_pass"
        assert user.role == "teacher"
        assert user.full_name == "Test User"
        assert user.specialty == "15.02.01"
        assert user.group_name == "Группа 101"
    
    def test_user_creation_with_minimal_fields(self):
        """Тест создания пользователя с минимальным набором полей"""
        user = User(
            user_id=2,
            username="minimal",
            password="pass",
            role="student",
            full_name="Minimal User"
        )
        
        assert user.id == 2
        assert user.username == "minimal"
        assert user.role == "student"
        assert user.full_name == "Minimal User"
        assert user.specialty is None
        assert user.group_name is None
    
    def test_user_repr(self):
        """Тест строкового представления пользователя"""
        user = User(1, "user", "pass", "teacher", "Test User")
        repr_str = repr(user)
        
        assert "User" in repr_str
        assert "user" in repr_str
        assert "Test User" in repr_str
    
    def test_user_equality(self):
        """Тест сравнения пользователей"""
        user1 = User(1, "user1", "pass", "teacher", "User One")
        user2 = User(1, "user1", "pass", "teacher", "User One")
        user3 = User(2, "user2", "pass", "student", "User Two")
        
        # Два пользователя с одинаковыми атрибутами считаются равными
        # (если не определен __eq__, то это тест на идентичность объектов)
        assert user1.id == user2.id
        assert user1.username == user2.username
        assert user1.id != user3.id

class TestSubjectModel:
    """Тесты для модели Subject"""
    
    def test_subject_creation(self):
        """Тест создания предмета"""
        subject = Subject(
            subject_id=1,
            name="Математика",
            code="МАТ-101",
            specialty="15.02.01"
        )
        
        assert subject.id == 1
        assert subject.name == "Математика"
        assert subject.code == "МАТ-101"
        assert subject.specialty == "15.02.01"
    
    def test_subject_without_code(self):
        """Тест создания предмета без кода"""
        subject = Subject(
            subject_id=2,
            name="Программирование",
            code=None,
            specialty="15.02.01"
        )
        
        assert subject.id == 2
        assert subject.name == "Программирование"
        assert subject.code is None
        assert subject.specialty == "15.02.01"

class TestGradeModel:
    """Тесты для модели Grade"""
    
    def test_grade_creation(self):
        """Тест создания оценки"""
        grade = Grade(
            grade_id=1,
            student_id=2,
            teacher_id=1,
            subject_id=3,
            grade_value=5,
            comment="Отличная работа! ПК 1.1 освоен",
            date="2024-01-15"
        )
        
        assert grade.id == 1
        assert grade.student_id == 2
        assert grade.teacher_id == 1
        assert grade.subject_id == 3
        assert grade.grade_value == 5
        assert grade.comment == "Отличная работа! ПК 1.1 освоен"
        assert grade.date == "2024-01-15"
    
    def test_grade_with_different_values(self):
        """Тест создания оценок с разными значениями"""
        test_cases = [
            (2, "Не сдал"),
            (3, "Удовлетворительно"),
            (4, "Хорошо"),
            (5, "Отлично")
        ]
        
        for grade_value, comment in test_cases:
            grade = Grade(
                grade_id=1,
                student_id=2,
                teacher_id=1,
                subject_id=3,
                grade_value=grade_value,
                comment=comment,
                date="2024-01-15"
            )
            
            assert grade.grade_value == grade_value
            assert grade.comment == comment
    
    def test_grade_date_format(self):
        """Тест формата даты оценки"""
        # Допустимые форматы даты
        valid_dates = [
            "2024-01-15",
            "2024-12-31",
            "2023-02-28"
        ]
        
        for date_str in valid_dates:
            grade = Grade(
                grade_id=1,
                student_id=2,
                teacher_id=1,
                subject_id=3,
                grade_value=4,
                comment="Test",
                date=date_str
            )
            
            assert grade.date == date_str