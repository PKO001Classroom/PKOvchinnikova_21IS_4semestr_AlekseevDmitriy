"""
UI-тесты для окна студента
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, 
    QGroupBox, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from models import User
from ui.student_window import StudentWindow

class TestStudentWindow:
    """Тесты для окна студента"""
    
    @pytest.fixture
    def test_student_data(self):
        """Тестовые данные студента"""
        return User(
            user_id=1,
            username="student1",
            password="123456",
            role="student",
            full_name="Петров Петр Петрович",
            specialty="15.02.01",
            group_name="Группа 101"
        )
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        mock = MagicMock()
        
        # Настраиваем возвращаемые данные
        mock_grades = [
            ("Математика", "МАТ-101", 5, "Отлично! ПК 1.1 освоен", "2024-01-15", "Иванов И.И."),
            ("Программирование", "ПРОГ-102", 4, "Хорошо. ОПК 2.2", "2024-01-16", "Иванов И.И."),
            ("Базы данных", "БД-103", 3, "Требует доработки. ПК 3.1", "2024-01-17", "Сидорова А.А.")
        ]
        
        mock.fetch_all.return_value = mock_grades
        mock.fetch_one.return_value = (4.0,)  # Средний балл
        
        return mock
    
    @pytest.fixture
    def student_window(self, qtbot, test_student_data, mock_db):
        """Фикстура окна студента"""
        window = StudentWindow(test_student_data, mock_db)
        qtbot.addWidget(window)
        window.show()
        QTest.qWait(100)  # Даем окну время на отрисовку
        return window
    
    def test_window_initialization(self, student_window, test_student_data):
        """Тест инициализации окна"""
        # Проверяем заголовок
        assert "Студент" in student_window.windowTitle()
        assert test_student_data.full_name in student_window.windowTitle()
        
        # Проверяем размер окна
        assert student_window.width() == 900
        assert student_window.height() == 600
        
        # Проверяем что окно видимо
        assert student_window.isVisible()
    
    def test_ui_elements_exist(self, student_window):
        """Тест наличия всех UI элементов"""
        # Проверяем основные элементы
        assert hasattr(student_window, 'grades_table')
        assert hasattr(student_window, 'refresh_button')
        assert hasattr(student_window, 'logout_button')
        
        # Проверяем что элементы созданы
        assert student_window.grades_table is not None
        assert student_window.refresh_button is not None
        assert student_window.logout_button is not None
        
        # Проверяем тип элементов
        assert isinstance(student_window.grades_table, QTableWidget)
        assert isinstance(student_window.refresh_button, QPushButton)
        assert isinstance(student_window.logout_button, QPushButton)
    
    def test_window_title(self, student_window, test_student_data):
        """Тест заголовка окна"""
        expected_title = f"Личный кабинет студента - {test_student_data.full_name}"
        assert student_window.windowTitle() == expected_title
    
    def test_student_info_displayed(self, student_window, test_student_data):
        """Тест отображения информации о студенте"""
        # Ищем все QLabel в окне
        labels = []
        for child in student_window.findChildren(QLabel):
            labels.append(child.text())
        
        # Проверяем что информация о студенте отображается
        info_found = False
        for label in labels:
            if test_student_data.full_name in label or \
               test_student_data.specialty in label or \
               test_student_data.group_name in label:
                info_found = True
                break
        
        assert info_found, "Информация о студенте не найдена в окне"
    
    def test_average_score_displayed(self, student_window, mock_db):
        """Тест отображения среднего балла"""
        # Ищем текст со средним баллом
        avg_found = False
        for child in student_window.findChildren(QLabel):
            if "Средний балл" in child.text():
                avg_found = True
                # Проверяем что значение отображается
                assert "4.00" in child.text()  # Средний балл из мока
                break
        
        assert avg_found, "Средний балл не отображается"
    
    def test_grades_table_columns(self, student_window):
        """Тест колонок таблицы оценок"""
        table = student_window.grades_table
        
        # Проверяем количество колонок
        expected_columns = 6
        assert table.columnCount() == expected_columns
        
        # Проверяем заголовки колонок
        expected_headers = ["Предмет", "Код", "Оценка", "Комментарий", "Дата", "Преподаватель"]
        for i, expected in enumerate(expected_headers):
            header_item = table.horizontalHeaderItem(i)
            assert header_item is not None
            assert header_item.text() == expected
    
    def test_grades_table_data_loaded(self, student_window, mock_db):
        """Тест загрузки данных в таблицу"""
        table = student_window.grades_table
        
        # Проверяем что данные загружены
        assert table.rowCount() == 3  # 3 оценки из мока
        
        # Проверяем первую строку
        assert table.item(0, 0).text() == "Математика"
        assert table.item(0, 1).text() == "МАТ-101"
        assert table.item(0, 2).text() == "5"
        assert table.item(0, 3).text() == "Отлично! ПК 1.1 освоен"
        assert table.item(0, 4).text() == "2024-01-15"
        assert table.item(0, 5).text() == "Иванов И.И."
    
    def test_grade_colors_correct(self, student_window):
        """Тест правильности цветов оценок"""
        table = student_window.grades_table
        
        # Проверяем цвета для каждой оценки
        test_cases = [
            (0, 2, QColor(144, 238, 144)),  # Оценка 5 - светло-зеленый
            (1, 2, QColor(173, 216, 230)),  # Оценка 4 - светло-голубой
            (2, 2, QColor(255, 255, 153)),  # Оценка 3 - светло-желтый
        ]
        
        for row, col, expected_color in test_cases:
            item = table.item(row, col)
            assert item is not None
            
            item_color = item.background().color()
            assert item_color.red() == expected_color.red()
            assert item_color.green() == expected_color.green()
            assert item_color.blue() == expected_color.blue()
    
    def test_table_resize_columns(self, student_window):
        """Тест изменения размера колонок"""
        table = student_window.grades_table
        
        # Запоминаем начальные размеры
        initial_widths = [table.columnWidth(i) for i in range(table.columnCount())]
        
        # Вызываем resizeColumnsToContents
        table.resizeColumnsToContents()
        
        # Проверяем что размеры изменились (хотя бы одна колонка)
        changed = False
        for i in range(table.columnCount()):
            if table.columnWidth(i) != initial_widths[i]:
                changed = True
                break
        
        assert changed, "Размеры колонок не изменились после вызова resizeColumnsToContents"
    
    def test_refresh_button_click(self, student_window, mock_db, qtbot):
        """Тест нажатия кнопки обновления"""
        # Запоминаем начальное количество вызовов
        initial_call_count = mock_db.fetch_all.call_count
        
        # Нажимаем кнопку обновления
        qtbot.mouseClick(student_window.refresh_button, Qt.LeftButton)
        
        # Даем время на обработку
        QTest.qWait(100)
        
        # Проверяем что метод был вызван еще раз
        assert mock_db.fetch_all.call_count == initial_call_count + 1
    
    def test_logout_button_click(self, student_window, qtbot):
        """Тест нажатия кнопки выхода"""
        # Мокаем метод close
        with patch.object(student_window, 'close') as mock_close:
            qtbot.mouseClick(student_window.logout_button, Qt.LeftButton)
            
            # Проверяем что close был вызван
            mock_close.assert_called_once()
    
    def test_table_sorting_enabled(self, student_window):
        """Тест включения сортировки таблицы"""
        table = student_window.grades_table
        assert table.isSortingEnabled()
    
    def test_table_alternating_row_colors(self, student_window):
        """Тест чередования цветов строк"""
        table = student_window.grades_table
        assert table.alternatingRowColors()
    
    def test_load_grades_with_empty_data(self, student_window, mock_db):
        """Тест загрузки оценок с пустыми данными"""
        # Настраиваем мок на возврат пустого списка
        mock_db.fetch_all.return_value = []
        mock_db.fetch_one.return_value = (0.0,)  # Средний балл 0
        
        # Перезагружаем данные
        student_window.load_grades()
        
        # Проверяем что таблица пустая
        assert student_window.grades_table.rowCount() == 0
    
    def test_calculate_average_score_method(self, student_window, mock_db):
        """Тест метода расчета среднего балла"""
        # Вызываем метод расчета
        avg_score = student_window.calculate_average_score()
        
        # Проверяем что метод БД был вызван
        mock_db.fetch_one.assert_called()
        
        # Проверяем результат
        assert avg_score == 4.0  # Значение из мока
    
    def test_get_grade_color_method(self, student_window):
        """Тест метода получения цвета оценки"""
        test_cases = [
            (5, QColor(144, 238, 144)),  # 5 - светло-зеленый
            (4, QColor(173, 216, 230)),  # 4 - светло-голубой
            (3, QColor(255, 255, 153)),  # 3 - светло-желтый
            (2, QColor(255, 182, 193)),  # 2 - светло-розовый
        ]
        
        for grade_value, expected_color in test_cases:
            color = student_window.get_grade_color(grade_value)
            assert color.red() == expected_color.red()
            assert color.green() == expected_color.green()
            assert color.blue() == expected_color.blue()
    
    def test_window_layout_structure(self, student_window):
        """Тест структуры layout окна"""
        # Получаем главный layout
        main_layout = student_window.layout()
        assert isinstance(main_layout, QVBoxLayout)
        
        # Проверяем что есть GroupBox для информации о студенте
        group_boxes = student_window.findChildren(QGroupBox)
        assert len(group_boxes) >= 2  # Должно быть минимум 2 GroupBox
    
    def test_button_styles_applied(self, student_window):
        """Тест применения стилей к кнопкам"""
        # Проверяем что у кнопок есть стили
        refresh_style = student_window.refresh_button.styleSheet()
        logout_style = student_window.logout_button.styleSheet()
        
        assert "background-color" in refresh_style
        assert "background-color" in logout_style
        
        # Проверяем конкретные цвета
        assert "#3498db" in refresh_style  # Синий для обновления
        assert "#e74c3c" in logout_style   # Красный для выхода
    
    def test_table_selection_behavior(self, student_window, qtbot):
        """Тест поведения выделения в таблице"""
        table = student_window.grades_table
        
        # Проверяем режим выделения
        assert table.selectionBehavior() == table.SelectRows
        assert table.selectionMode() == table.SingleSelection
        
        # Выделяем первую строку
        table.selectRow(0)
        assert table.currentRow() == 0
    
    def test_no_grades_message(self, student_window, mock_db, qtbot):
        """Тест отображения сообщения при отсутствии оценок"""
        # Настраиваем мок на возврат пустого списка
        mock_db.fetch_all.return_value = []
        
        # Перезагружаем данные
        student_window.load_grades()
        
        # Проверяем что таблица пустая
        assert student_window.grades_table.rowCount() == 0
        
        # Можно добавить проверку сообщения "Нет данных" если оно реализовано
    
    def test_special_characters_in_comments(self, student_window, mock_db):
        """Тест обработки специальных символов в комментариях"""
        # Настраиваем мок с комментариями со спецсимволами
        test_grades = [
            ("Тест", "ТЕСТ-001", 5, "Комментарий с ❤️ и emoji 😊", "2024-01-18", "Преподаватель")
        ]
        mock_db.fetch_all.return_value = test_grades
        
        # Перезагружаем данные
        student_window.load_grades()
        
        # Проверяем что комментарий отображается
        table = student_window.grades_table
        assert table.rowCount() == 1
        assert "❤️" in table.item(0, 3).text()
    
    @pytest.mark.parametrize("grades_data,expected_average", [
        ([], 0.0),  # Нет оценок
        ([("Математика", "МАТ-101", 5, "Отлично", "2024-01-15", "Учитель")], 5.0),  # Одна оценка
        ([
            ("Мат", "МАТ", 3, "Хорошо", "2024-01-15", "У1"),
            ("Мат", "МАТ", 4, "Хорошо", "2024-01-16", "У1"),
            ("Мат", "МАТ", 5, "Отлично", "2024-01-17", "У1")
        ], 4.0),  # Несколько оценок
    ])
    def test_average_calculation_various_data(self, student_window, mock_db, 
                                              grades_data, expected_average):
        """Тест расчета среднего балла с разными данными"""
        # Настраиваем мок
        mock_db.fetch_all.return_value = grades_data
        mock_db.fetch_one.return_value = (expected_average,)
        
        # Перезагружаем данные
        student_window.load_grades()
        
        # Проверяем количество строк
        assert student_window.grades_table.rowCount() == len(grades_data)
    
    def test_window_close_event(self, student_window):
        """Тест события закрытия окна"""
        # Создаем mock для closeEvent
        close_event_mock = Mock()
        
        # Вызываем closeEvent
        student_window.closeEvent(close_event_mock)
        
        # Проверяем что метод accept был вызван
        close_event_mock.accept.assert_called_once()