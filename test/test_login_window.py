"""
UI-тесты для окна входа
"""
import pytest
from PyQt5.QtWidgets import QLineEdit, QComboBox, QPushButton, QLabel
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from ui.login_window import LoginWindow

class TestLoginWindowUI:
    """UI-тесты окна входа"""
    
    def test_window_properties(self, qtbot, mock_db):
        """Тест свойств окна"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Проверяем заголовок
        assert "Учебный журнал" in window.windowTitle()
        assert "Вход" in window.windowTitle()
        
        # Проверяем размер
        assert window.width() == 400
        assert window.height() == 300
        assert window.isFixedSize()  # Размер фиксирован
    
    def test_ui_elements_existence(self, qtbot, mock_db):
        """Тест наличия всех UI элементов"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Проверяем наличие полей ввода
        assert isinstance(window.login_input, QLineEdit)
        assert isinstance(window.password_input, QLineEdit)
        assert isinstance(window.role_combo, QComboBox)
        
        # Проверяем наличие кнопок
        assert isinstance(window.login_button, QPushButton)
        assert isinstance(window.exit_button, QPushButton)
        
        # Проверяем текст кнопок
        assert window.login_button.text() == "Войти"
        assert window.exit_button.text() == "Выход"
    
    def test_password_field_is_masked(self, qtbot, mock_db):
        """Тест что поле пароля скрыто"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        assert window.password_input.echoMode() == QLineEdit.Password
    
    def test_role_combobox_content(self, qtbot, mock_db):
        """Тест содержания выпадающего списка ролей"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        assert window.role_combo.count() == 2
        assert window.role_combo.itemText(0) == "teacher"
        assert window.role_combo.itemText(1) == "student"
        assert window.role_combo.currentText() == "teacher"  # По умолчанию
    
    def test_input_fields_placeholders(self, qtbot, mock_db):
        """Тест текста-подсказки в полях"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        assert "Введите логин" in window.login_input.placeholderText()
        assert "Введите пароль" in window.password_input.placeholderText()
    
    def test_help_text_exists(self, qtbot, mock_db):
        """Тест наличия справочного текста"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Ищем все QLabel с текстом о тестовых данных
        help_labels = []
        for child in window.findChildren(QLabel):
            if "Тестовые данные" in child.text():
                help_labels.append(child)
        
        assert len(help_labels) > 0
    
    def test_button_styles(self, qtbot, mock_db):
        """Тест стилей кнопок"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        login_style = window.login_button.styleSheet()
        exit_style = window.exit_button.styleSheet()
        
        # Проверяем что стили применены
        assert "background-color" in login_style
        assert "background-color" in exit_style
        
        # Проверяем цвета кнопок
        assert "#4CAF50" in login_style  # Зеленый для входа
        assert "#f44336" in exit_style   # Красный для выхода
    
    def test_field_validation_ui_feedback(self, qtbot, mock_db):
        """Тест UI-обратной связи при валидации"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Вводим текст в поля
        test_login = "testuser123"
        test_password = "testpass123"
        
        window.login_input.setText(test_login)
        window.password_input.setText(test_password)
        
        # Проверяем что текст установлен
        assert window.login_input.text() == test_login
        assert window.password_input.text() == test_password
    
    def test_tab_order(self, qtbot, mock_db):
        """Тест порядка перехода по Tab"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Устанавливаем фокус на поле логина
        window.login_input.setFocus()
        assert window.login_input.hasFocus()
        
        # Нажимаем Tab
        qtbot.keyClick(window.login_input, Qt.Key_Tab)
        assert window.password_input.hasFocus()
        
        qtbot.keyClick(window.password_input, Qt.Key_Tab)
        assert window.role_combo.hasFocus()
        
        qtbot.keyClick(window.role_combo, Qt.Key_Tab)
        assert window.login_button.hasFocus()
        
        qtbot.keyClick(window.login_button, Qt.Key_Tab)
        assert window.exit_button.hasFocus()
    
    def test_enter_key_in_password_field(self, qtbot, mock_db):
        """Тест что Enter в поле пароля вызывает вход"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Заполняем поля
        window.login_input.setText("test")
        window.password_input.setText("test")
        
        # Мокаем метод login
        import ui.login_window
        original_login = window.login
        
        login_called = False
        def mock_login():
            nonlocal login_called
            login_called = True
        
        window.login = mock_login
        
        try:
            # Нажимаем Enter в поле пароля
            qtbot.keyClick(window.password_input, Qt.Key_Return)
            
            # Проверяем что login был вызван
            assert login_called is True
        finally:
            window.login = original_login
    
    @pytest.mark.parametrize("login,password,role", [
        ("teacher1", "123456", "teacher"),
        ("student1", "123456", "student"),
        ("", "", "teacher"),  # Пустые поля
        ("user", "", "student"),  # Только пароль пустой
        ("", "pass", "teacher"),  # Только логин пустой
    ])
    def test_input_combinations(self, qtbot, mock_db, login, password, role):
        """Тест различных комбинаций ввода"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Заполняем поля
        window.login_input.setText(login)
        window.password_input.setText(password)
        window.role_combo.setCurrentText(role)
        
        # Проверяем что значения установлены
        assert window.login_input.text() == login
        assert window.password_input.text() == password
        assert window.role_combo.currentText() == role