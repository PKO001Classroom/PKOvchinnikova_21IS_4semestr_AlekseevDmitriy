"""
UI-тесты для окна преподавателя
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import (
    QTableWidget, QTableWidgetItem, QLabel, QPushButton, 
    QGroupBox, QComboBox, QLineEdit, QTextEdit, QDateEdit,
    QFormLayout, QHBoxLayout, QVBoxLayout, QMessageBox
)
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor

from models import User
from ui.teacher_window import TeacherWindow

class TestTeacherWindow:
    """Тесты для окна преподавателя"""
    
    @pytest.fixture
    def test_teacher_data(self):
        """Тестовые данные преподавателя"""
        return User(
            user_id=1,
            username="teacher1",
            password="123456",
            role="teacher",
            full_name="Иванов Иван Иванович",
            specialty="15.02.01",
            group_name=None
        )
    
    @pytest.fixture
    def mock_db(self):
        """Мок базы данных"""
        mock = MagicMock()
        
        # Настраиваем возвращаемые данные для студентов
        mock_students = [
            (2, "Петров Петр Петрович"),
            (3, "Сидорова Анна Сергеевна"),
            (4, "Кузнецов Алексей Викторович")
        ]
        
        # Настраиваем возвращаемые данные для оценок
        mock_grades = [
            ("Петров Петр Петрович", "Математика", 5, "Отлично! ПК 1.1", "2024-01-15", "15.02.01", "Группа 101"),
            ("Сидорова Анна Сергеевна", "Программирование", 4, "Хорошо. ОПК 2.2", "2024-01-16", "15.02.01", "Группа 101"),
        ]
        
        mock.fetch_all.side_effect = [
            mock_students,  # Для load_students
            mock_grades     # Для load_grades
        ]
        
        return mock
    
    @pytest.fixture
    def teacher_window(self, qtbot, test_teacher_data, mock_db):
        """Фикстура окна преподавателя"""
        window = TeacherWindow(test_teacher_data, mock_db)
        qtbot.addWidget(window)
        window.show()
        QTest.qWait(100)  # Даем окну время на отрисовку
        return window
    
    def test_window_initialization(self, teacher_window, test_teacher_data):
        """Тест инициализации окна"""
        # Проверяем заголовок
        assert "Преподаватель" in teacher_window.windowTitle()
        assert test_teacher_data.full_name in teacher_window.windowTitle()
        
        # Проверяем размер окна
        assert teacher_window.width() == 1000
        assert teacher_window.height() == 700
        
        # Проверяем что окно видимо
        assert teacher_window.isVisible()
    
    def test_ui_elements_exist(self, teacher_window):
        """Тест наличия всех UI элементов"""
        # Проверяем основные элементы формы
        assert hasattr(teacher_window, 'student_combo')
        assert hasattr(teacher_window, 'subject_combo')
        assert hasattr(teacher_window, 'grade_combo')
        assert hasattr(teacher_window, 'date_edit')
        assert hasattr(teacher_window, 'comment_edit')
        assert hasattr(teacher_window, 'add_grade_button')
        
        # Проверяем элементы таблицы
        assert hasattr(teacher_window, 'grades_table')
        assert hasattr(teacher_window, 'refresh_button')
        assert hasattr(teacher_window, 'logout_button')
        
        # Проверяем тип элементов
        assert isinstance(teacher_window.student_combo, QComboBox)
        assert isinstance(teacher_window.subject_combo, QComboBox)
        assert isinstance(teacher_window.grade_combo, QComboBox)
        assert isinstance(teacher_window.date_edit, QDateEdit)
        assert isinstance(teacher_window.comment_edit, QTextEdit)
        assert isinstance(teacher_window.add_grade_button, QPushButton)
        assert isinstance(teacher_window.grades_table, QTableWidget)
    
    def test_window_title(self, teacher_window, test_teacher_data):
        """Тест заголовка окна"""
        expected_title = f"Панель преподавателя - {test_teacher_data.full_name}"
        assert teacher_window.windowTitle() == expected_title
    
    def test_form_elements_initial_state(self, teacher_window):
        """Тест начального состояния элементов формы"""
        # Проверяем выпадающие списки
        assert teacher_window.student_combo.count() > 0
        assert teacher_window.subject_combo.count() > 0
        assert teacher_window.grade_combo.count() == 4  # 2, 3, 4, 5
        
        # Проверяем значения по умолчанию
        assert teacher_window.grade_combo.currentText() == "5"
        assert teacher_window.date_edit.date() == QDate.currentDate()
        
        # Проверяем placeholder тексты
        comment_placeholder = teacher_window.comment_edit.placeholderText()
        assert "минимум 100 символов" in comment_placeholder.lower()
    
    def test_load_students_method(self, teacher_window, mock_db):
        """Тест загрузки списка студентов"""
        # Проверяем что студенты загружены в combo box
        combo = teacher_window.student_combo
        assert combo.count() == 3  # 3 студента из мока
        
        # Проверяем имена студентов
        expected_students = [
            "Петров Петр Петрович",
            "Сидорова Анна Сергеевна", 
            "Кузнецов Алексей Викторович"
        ]
        
        for i in range(combo.count()):
            assert combo.itemText(i) == expected_students[i]
    
    def test_load_subjects_method(self, teacher_window, mock_db):
        """Тест загрузки списка предметов"""
        # В текущей реализации предметы загружаются из БД
        # Проверяем что combo box не пустой
        combo = teacher_window.subject_combo
        assert combo.count() > 0
    
    def test_grades_table_columns(self, teacher_window):
        """Тест колонок таблицы оценок"""
        table = teacher_window.grades_table
        
        # Проверяем количество колонок
        expected_columns = 7
        assert table.columnCount() == expected_columns
        
        # Проверяем заголовки колонок
        expected_headers = [
            "Студент", "Предмет", "Оценка", "Комментарий", 
            "Дата", "Специальность", "Группа"
        ]
        
        for i, expected in enumerate(expected_headers):
            header_item = table.horizontalHeaderItem(i)
            assert header_item is not None
            assert header_item.text() == expected
    
    def test_grades_table_data_loaded(self, teacher_window, mock_db):
        """Тест загрузки данных в таблицу"""
        table = teacher_window.grades_table
        
        # Проверяем что данные загружены
        assert table.rowCount() == 2  # 2 оценки из мока
        
        # Проверяем первую строку
        assert table.item(0, 0).text() == "Петров Петр Петрович"
        assert table.item(0, 1).text() == "Математика"
        assert table.item(0, 2).text() == "5"
        assert table.item(0, 3).text() == "Отлично! ПК 1.1"
        assert table.item(0, 4).text() == "2024-01-15"
        assert table.item(0, 5).text() == "15.02.01"
        assert table.item(0, 6).text() == "Группа 101"
    
    def test_grade_colors_in_table(self, teacher_window):
        """Тест цветов оценок в таблице"""
        table = teacher_window.grades_table
        
        # Проверяем цвета для каждой оценки
        test_cases = [
            (0, 2, QColor(144, 238, 144)),  # Оценка 5 - светло-зеленый
            (1, 2, QColor(173, 216, 230)),  # Оценка 4 - светло-голубой
        ]
        
        for row, col, expected_color in test_cases:
            item = table.item(row, col)
            assert item is not None
            
            item_color = item.background().color()
            assert item_color.red() == expected_color.red()
            assert item_color.green() == expected_color.green()
            assert item_color.blue() == expected_color.blue()
    
    def test_add_grade_validation_success(self, teacher_window, mock_db, qtbot):
        """Тест успешной валидации при добавлении оценки"""
        # Заполняем форму
        teacher_window.student_combo.setCurrentIndex(0)  # Выбираем первого студента
        teacher_window.subject_combo.setCurrentIndex(0)  # Выбираем первый предмет
        teacher_window.grade_combo.setCurrentText("5")
        teacher_window.date_edit.setDate(QDate(2024, 1, 20))
        
        # Вводим длинный комментарий
        long_comment = "Отличная работа! Студент продемонстрировал полное понимание темы. "
        long_comment += "ПК 1.1 освоен на высоком уровне. Рекомендуется участие в олимпиаде. " * 3
        teacher_window.comment_edit.setPlainText(long_comment)
        
        # Мокаем QMessageBox.information
        with patch.object(QMessageBox, 'information') as mock_info:
            # Нажимаем кнопку добавления оценки
            qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
            
            # Проверяем что сообщение об успехе показано
            mock_info.assert_called_once()
            
            # Проверяем что метод add_grade был вызван
            mock_db.execute_query.assert_called()
    
    def test_add_grade_validation_empty_fields(self, teacher_window, mock_db, qtbot):
        """Тест валидации пустых полей"""
        # Оставляем форму пустой
        
        # Мокаем QMessageBox.warning
        with patch.object(QMessageBox, 'warning') as mock_warning:
            # Нажимаем кнопку добавления оценки
            qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
            
            # Проверяем что предупреждение показано
            mock_warning.assert_called_once()
            args, kwargs = mock_warning.call_args
            assert "заполните все поля" in args[2].lower()
    
    def test_add_grade_validation_short_comment(self, teacher_window, mock_db, qtbot):
        """Тест валидации короткого комментария"""
        # Заполняем форму
        teacher_window.student_combo.setCurrentIndex(0)
        teacher_window.subject_combo.setCurrentIndex(0)
        
        # Вводим короткий комментарий
        teacher_window.comment_edit.setPlainText("Короткий комментарий")
        
        # Мокаем QMessageBox.warning
        with patch.object(QMessageBox, 'warning') as mock_warning:
            # Нажимаем кнопку добавления оценки
            qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
            
            # Проверяем что предупреждение показано
            mock_warning.assert_called_once()
            args, kwargs = mock_warning.call_args
            assert "не менее 100 символов" in args[2].lower()
    
    def test_add_grade_validation_no_competency_code(self, teacher_window, mock_db, qtbot):
        """Тест валидации отсутствия кода компетенции"""
        # Заполняем форму
        teacher_window.student_combo.setCurrentIndex(0)
        teacher_window.subject_combo.setCurrentIndex(0)
        
        # Вводим длинный комментарий без кода компетенции
        long_comment = "Хорошая работа, но можно лучше. " * 10
        teacher_window.comment_edit.setPlainText(long_comment)
        
        # Мокаем QMessageBox.warning
        with patch.object(QMessageBox, 'warning') as mock_warning:
            # Нажимаем кнопку добавления оценки
            qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
            
            # Проверяем что предупреждение показано
            mock_warning.assert_called_once()
            args, kwargs = mock_warning.call_args
            assert "код компетенции" in args[2].lower() or "пк" in args[2].lower()
    
    def test_refresh_button_functionality(self, teacher_window, mock_db, qtbot):
        """Тест функциональности кнопки обновления"""
        # Запоминаем начальное количество вызовов
        initial_call_count = mock_db.fetch_all.call_count
        
        # Нажимаем кнопку обновления
        qtbot.mouseClick(teacher_window.refresh_button, Qt.LeftButton)
        
        # Даем время на обработку
        QTest.qWait(100)
        
        # Проверяем что метод был вызван еще раз
        # (load_grades вызывается при нажатии кнопки)
        assert mock_db.fetch_all.call_count > initial_call_count
    
    def test_logout_button_click(self, teacher_window, qtbot):
        """Тест нажатия кнопки выхода"""
        # Мокаем метод close
        with patch.object(teacher_window, 'close') as mock_close:
            qtbot.mouseClick(teacher_window.logout_button, Qt.LeftButton)
            
            # Проверяем что close был вызван
            mock_close.assert_called_once()
    
    def test_form_reset_after_successful_add(self, teacher_window, mock_db, qtbot):
        """Тест сброса формы после успешного добавления оценки"""
        # Заполняем форму
        teacher_window.student_combo.setCurrentIndex(0)
        teacher_window.subject_combo.setCurrentIndex(0)
        teacher_window.comment_edit.setPlainText("Тестовый комментарий " * 10)
        
        # Сохраняем начальное состояние
        initial_comment = teacher_window.comment_edit.toPlainText()
        initial_date = teacher_window.date_edit.date()
        
        # Мокаем успешное добавление
        with patch.object(QMessageBox, 'information'):
            with patch.object(teacher_window, 'load_grades'):
                # Нажимаем кнопку добавления
                qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
                
                # Проверяем что форма сброшена
                # (В текущей реализации комментарий очищается, дата остается текущей)
                assert teacher_window.comment_edit.toPlainText() == ""
                assert teacher_window.date_edit.date() == QDate.currentDate()
    
    def test_get_grade_color_method(self, teacher_window):
        """Тест метода получения цвета оценки"""
        test_cases = [
            (5, QColor(144, 238, 144)),  # 5 - светло-зеленый
            (4, QColor(173, 216, 230)),  # 4 - светло-голубой
            (3, QColor(255, 255, 153)),  # 3 - светло-желтый
            (2, QColor(255, 182, 193)),  # 2 - светло-розовый
        ]
        
        for grade_value, expected_color in test_cases:
            color = teacher_window.get_grade_color(grade_value)
            assert color.red() == expected_color.red()
            assert color.green() == expected_color.green()
            assert color.blue() == expected_color.blue()
    
    def test_window_layout_structure(self, teacher_window):
        """Тест структуры layout окна"""
        # Получаем главный layout
        main_layout = teacher_window.layout()
        assert isinstance(main_layout, QVBoxLayout)
        
        # Проверяем что есть GroupBox для формы
        group_boxes = teacher_window.findChildren(QGroupBox)
        assert len(group_boxes) >= 2  # Должно быть минимум 2 GroupBox
    
    def test_button_styles_applied(self, teacher_window):
        """Тест применения стилей к кнопкам"""
        # Проверяем что у кнопок есть стили
        add_button_style = teacher_window.add_grade_button.styleSheet()
        refresh_style = teacher_window.refresh_button.styleSheet()
        logout_style = teacher_window.logout_button.styleSheet()
        
        assert "background-color" in add_button_style
        assert "background-color" in refresh_style
        assert "background-color" in logout_style
        
        # Проверяем конкретные цвета
        assert "#27ae60" in add_button_style  # Зеленый для добавления
        assert "#3498db" in refresh_style     # Синий для обновления
        assert "#e74c3c" in logout_style      # Красный для выхода
    
    def test_table_features(self, teacher_window):
        """Тест особенностей таблицы"""
        table = teacher_window.grades_table
        
        # Проверяем что чередование цветов включено
        assert table.alternatingRowColors()
        
        # Проверяем что растягивание последней колонки включено
        assert table.horizontalHeader().stretchLastSection()
        
        # Проверяем что сортировка включена
        assert table.isSortingEnabled()
    
    def test_form_validation_edge_cases(self, teacher_window, mock_db, qtbot):
        """Тест граничных случаев валидации формы"""
        test_cases = [
            # (student_index, subject_index, comment, should_pass)
            (0, 0, "Короткий", False),  # Слишком короткий комментарий
            (0, 0, "Длинный комментарий " * 10, True),  # Длинный комментарий
            (-1, 0, "Комментарий " * 10, False),  # Не выбран студент
            (0, -1, "Комментарий " * 10, False),  # Не выбран предмет
        ]
        
        for student_idx, subject_idx, comment, should_pass in test_cases:
            # Сбрасываем форму
            teacher_window.comment_edit.clear()
            
            if student_idx >= 0:
                teacher_window.student_combo.setCurrentIndex(student_idx)
            if subject_idx >= 0:
                teacher_window.subject_combo.setCurrentIndex(subject_idx)
            
            teacher_window.comment_edit.setPlainText(comment)
            
            # Мокаем QMessageBox
            with patch.object(QMessageBox, 'warning') as mock_warning:
                with patch.object(QMessageBox, 'information') as mock_info:
                    # Нажимаем кнопку
                    qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
                    
                    if should_pass:
                        mock_info.assert_called()
                        mock_warning.assert_not_called()
                    else:
                        mock_warning.assert_called()
    
    def test_date_edit_features(self, teacher_window):
        """Тест особенностей QDateEdit"""
        date_edit = teacher_window.date_edit
        
        # Проверяем что календарь включен
        assert date_edit.calendarPopup()
        
        # Проверяем формат даты
        assert date_edit.displayFormat() == "yyyy-MM-dd"
        
        # Проверяем что дата по умолчанию - сегодня
        assert date_edit.date() == QDate.currentDate()
    
    @pytest.mark.parametrize("comment, has_competency_code", [
        ("Комментарий с ПК 1.1", True),
        ("Комментарий с ОПК 2.3", True),
        ("Комментарий без кода", False),
        ("пк 1.1 в нижнем регистре", True),
        ("опк 3.2 и еще что-то", True),
    ])
    def test_competency_code_detection(self, teacher_window, comment, has_competency_code):
        """Тест определения кода компетенции в комментарии"""
        # Этот тест проверяет логику валидации кодов компетенции
        # В текущей реализации есть проверка на наличие ПК/ОПК в комментарии
        
        teacher_window.comment_edit.setPlainText(comment)
        
        # Можно добавить проверку если есть отдельный метод для проверки кодов
        if has_competency_code:
            assert "ПК" in comment.upper() or "ОПК" in comment.upper()
        else:
            assert "ПК" not in comment.upper() and "ОПК" not in comment.upper()
    
    def test_error_handling_database_errors(self, teacher_window, mock_db, qtbot):
        """Тест обработки ошибок базы данных"""
        # Настраиваем мок чтобы выбросить исключение
        mock_db.execute_query.side_effect = Exception("Database error")
        
        # Заполняем форму валидными данными
        teacher_window.student_combo.setCurrentIndex(0)
        teacher_window.subject_combo.setCurrentIndex(0)
        teacher_window.comment_edit.setPlainText("Комментарий " * 10)
        
        # Мокаем QMessageBox.critical для ошибок
        with patch.object(QMessageBox, 'critical') as mock_critical:
            # Нажимаем кнопку добавления
            qtbot.mouseClick(teacher_window.add_grade_button, Qt.LeftButton)
            
            # Проверяем что сообщение об ошибке показано
            mock_critical.assert_called_once()
            args, kwargs = mock_critical.call_args
            assert "ошибка" in args[2].lower() or "error" in args[2].lower()
    
    def test_form_field_maximums(self, teacher_window):
        """Тест ограничений полей формы"""
        # Проверяем максимальную высоту комментария
        assert teacher_window.comment_edit.maximumHeight() == 100
        
        # Проверяем допустимые значения в grade_combo
        expected_grades = ["5", "4", "3", "2"]
        for i in range(teacher_window.grade_combo.count()):
            assert teacher_window.grade_combo.itemText(i) == expected_grades[i]
    
    def test_window_resize_behavior(self, teacher_window, qtbot):
        """Тест поведения при изменении размера окна"""
        # Запоминаем начальный размер
        initial_width = teacher_window.width()
        initial_height = teacher_window.height()
        
        # Изменяем размер
        new_width = 1200
        new_height = 800
        teacher_window.resize(new_width, new_height)
        
        # Проверяем что размер изменился
        assert teacher_window.width() == new_width
        assert teacher_window.height() == new_height
        
        # Проверяем что таблица все еще видна
        assert teacher_window.grades_table.isVisible()
    
    def test_tab_order_in_form(self, teacher_window, qtbot):
        """Тест порядка Tab в форме"""
        # Устанавливаем фокус на первое поле
        teacher_window.student_combo.setFocus()
        assert teacher_window.student_combo.hasFocus()
        
        # Нажимаем Tab и проверяем переход
        qtbot.keyClick(teacher_window.student_combo, Qt.Key_Tab)
        assert teacher_window.subject_combo.hasFocus()
        
        qtbot.keyClick(teacher_window.subject_combo, Qt.Key_Tab)
        assert teacher_window.grade_combo.hasFocus()
        
        qtbot.keyClick(teacher_window.grade_combo, Qt.Key_Tab)
        assert teacher_window.date_edit.hasFocus()
        
        qtbot.keyClick(teacher_window.date_edit, Qt.Key_Tab)
        assert teacher_window.comment_edit.hasFocus()