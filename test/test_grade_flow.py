"""
Интеграционные тесты потока работы с оценками
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# Импортируем после добавления пути в conftest
from models import User
from ui.teacher_window import TeacherWindow
from ui.student_window import StudentWindow

class TestGradeFlowIntegration:
    """Интеграционные тесты потока оценок"""
    
    def test_teacher_can_add_valid_grade(self, qtbot, mock_db, teacher_user_data):
        """Тест что преподаватель может добавить валидную оценку"""
        # Создаем пользователя-преподавателя
        teacher_user = User(**teacher_user_data)
        
        # Создаем окно преподавателя
        window = TeacherWindow(teacher_user, mock_db)
        qtbot.addWidget(window)
        
        # Заполняем форму
        window.student_input.setText("Test Student")
        window.subject_input.setText("Test Subject")
        window.grade_combo.setCurrentText("5")
        window.comment_input.setText("Отличная работа! ПК 1.1 освоен. " * 5)  # Длинный комментарий
        
        # Мокаем QMessageBox.information
        success_messages = []
        def mock_information(parent, title, message):
            success_messages.append(message)
            return QMessageBox.Information
        
        with patch.object(QMessageBox, 'information', mock_information):
            # Находим и нажимаем кнопку добавления оценки
            for child in window.findChildren(type(window)):
                if hasattr(child, 'text') and child.text() == "Добавить оценку":
                    qtbot.mouseClick(child, Qt.LeftButton)
                    break
            
            # Проверяем что сообщение об успехе было показано
            assert len(success_messages) == 1
            assert "успешно добавлена" in success_messages[0].lower()
            
            # Проверяем что метод add_grade был вызван
            mock_db.add_grade.assert_called_once()
    
    def test_grade_validation_short_comment(self, qtbot, mock_db, teacher_user_data):
        """Тест валидации короткого комментария"""
        teacher_user = User(**teacher_user_data)
        window = TeacherWindow(teacher_user, mock_db)
        qtbot.addWidget(window)
        
        # Заполняем форму с коротким комментарием
        window.student_input.setText("Test Student")
        window.subject_input.setText("Test Subject")
        window.grade_combo.setCurrentText("4")
        window.comment_input.setText("ок")  # Слишком коротко
        
        # Мокаем QMessageBox.warning
        warning_messages = []
        def mock_warning(parent, title, message):
            warning_messages.append(message)
            return QMessageBox.Warning
        
        with patch.object(QMessageBox, 'warning', mock_warning):
            # Находим и нажимаем кнопку добавления оценки
            for child in window.findChildren(type(window)):
                if hasattr(child, 'text') and child.text() == "Добавить оценку":
                    qtbot.mouseClick(child, Qt.LeftButton)
                    break
            
            # Проверяем что предупреждение было показано
            assert len(warning_messages) == 1
            assert "не менее 10 символов" in warning_messages[0]
            
            # Проверяем что метод add_grade НЕ был вызван
            mock_db.add_grade.assert_not_called()
    
    def test_empty_fields_validation_in_grade_form(self, qtbot, mock_db, teacher_user_data):
        """Тест валидации пустых полей в форме оценки"""
        teacher_user = User(**teacher_user_data)
        window = TeacherWindow(teacher_user, mock_db)
        qtbot.addWidget(window)
        
        # Оставляем поля пустыми
        
        # Мокаем QMessageBox.warning
        warning_messages = []
        def mock_warning(parent, title, message):
            warning_messages.append(message)
            return QMessageBox.Warning
        
        with patch.object(QMessageBox, 'warning', mock_warning):
            # Нажимаем кнопку добавления оценки
            for child in window.findChildren(type(window)):
                if hasattr(child, 'text') and child.text() == "Добавить оценку":
                    qtbot.mouseClick(child, Qt.LeftButton)
                    break
            
            # Проверяем что предупреждение было показано
            assert len(warning_messages) == 1
            assert "заполните все поля" in warning_messages[0].lower()
    
    def test_student_can_view_grades(self, qtbot, mock_db, test_user_data):
        """Тест что студент может просматривать оценки"""
        student_user = User(**test_user_data)
        
        # Настраиваем мок БД для возврата тестовых оценок
        test_grades = [
            ("Математика", 5, "Отлично! ПК 1.1", "2024-01-15"),
            ("Программирование", 4, "Хорошо. ОПК 2.2", "2024-01-16"),
            ("Базы данных", 3, "Нужно подтянуть", "2024-01-17")
        ]
        mock_db.get_student_grades.return_value = test_grades
        mock_db.fetch_one.return_value = (4.0,)  # Средний балл
        
        # Создаем окно студента
        window = StudentWindow(student_user, mock_db)
        qtbot.addWidget(window)
        
        # Проверяем что данные загружены в таблицу
        table = window.grades_table
        assert table.rowCount() == 3
        
        # Проверяем первую строку
        assert table.item(0, 0).text() == "Математика"
        assert table.item(0, 1).text() == "5"
        assert table.item(0, 2).text() == "Отлично! ПК 1.1"
        assert table.item(0, 3).text() == "2024-01-15"
        
        # Проверяем цвета оценок
        grade_5_item = table.item(0, 1)
        grade_4_item = table.item(1, 1)
        grade_3_item = table.item(2, 1)
        
        assert grade_5_item.background().color() == QColor(144, 238, 144)  # Светло-зеленый
        assert grade_4_item.background().color() == QColor(173, 216, 230)  # Светло-голубой
        assert grade_3_item.background().color() == QColor(255, 255, 153)  # Светло-желтый
    
    def test_refresh_functionality(self, qtbot, mock_db, test_user_data):
        """Тест функциональности обновления данных"""
        student_user = User(**test_user_data)
        window = StudentWindow(student_user, mock_db)
        qtbot.addWidget(window)
        
        # Запоминаем начальное количество вызовов
        initial_call_count = mock_db.get_student_grades.call_count
        
        # Нажимаем кнопку обновления
        qtbot.mouseClick(window.refresh_button, Qt.LeftButton)
        
        # Проверяем что метод был вызван еще раз
        assert mock_db.get_student_grades.call_count == initial_call_count + 1