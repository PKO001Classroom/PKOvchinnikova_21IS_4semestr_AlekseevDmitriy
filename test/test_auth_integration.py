"""
Интеграционные тесты потока авторизации
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Импортируем после добавления пути в conftest
from ui.login_window import LoginWindow
from models import User

class TestAuthIntegration:
    """Интеграционные тесты авторизации"""
    
    def test_successful_login_flow(self, qtbot, mock_db):
        """Тест успешного потока входа"""
        # Создаем окно входа
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Заполняем форму
        window.login_input.setText("test_user")
        window.password_input.setText("test_pass")
        window.role_combo.setCurrentText("student")
        
        # Мокаем on_login_success для проверки вызова
        login_called = []
        def mock_on_login(user):
            login_called.append(user)
        
        window.on_login_success = mock_on_login
        
        # Нажимаем кнопку входа
        qtbot.mouseClick(window.login_button, Qt.LeftButton)
        
        # Проверяем что on_login_success был вызван
        assert len(login_called) == 1
        user = login_called[0]
        assert isinstance(user, User)
        assert user.username == "test_user"
        assert user.role == "student"
    
    def test_failed_login_wrong_credentials(self, qtbot, mock_db):
        """Тест неудачного входа с неверными данными"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Настраиваем мок БД чтобы вернуть None (неверные данные)
        mock_db.check_user.return_value = None
        
        # Мокаем QMessageBox.critical
        error_messages = []
        def mock_critical(parent, title, message):
            error_messages.append(message)
            return QMessageBox.Critical
        
        with patch.object(QMessageBox, 'critical', mock_critical):
            # Заполняем форму неверными данными
            window.login_input.setText("wrong_user")
            window.password_input.setText("wrong_pass")
            window.role_combo.setCurrentText("student")
            
            qtbot.mouseClick(window.login_button, Qt.LeftButton)
            
            # Проверяем что сообщение об ошибке было показано
            assert len(error_messages) == 1
            assert "Неверный логин или пароль" in error_messages[0]
    
    def test_empty_fields_validation(self, qtbot, mock_db):
        """Тест валидации пустых полей"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Мокаем QMessageBox.warning
        warning_messages = []
        def mock_warning(parent, title, message):
            warning_messages.append(message)
            return QMessageBox.Warning
        
        with patch.object(QMessageBox, 'warning', mock_warning):
            # Оставляем поля пустыми и нажимаем вход
            qtbot.mouseClick(window.login_button, Qt.LeftButton)
            
            # Проверяем что предупреждение было показано
            assert len(warning_messages) == 1
            assert "заполните все поля" in warning_messages[0].lower()
    
    def test_exit_button_functionality(self, qtbot, mock_db):
        """Тест работы кнопки выхода"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Мокаем метод close
        with patch.object(window, 'close') as mock_close:
            qtbot.mouseClick(window.exit_button, Qt.LeftButton)
            mock_close.assert_called_once()
    
    def test_keyboard_navigation(self, qtbot, mock_db):
        """Тест навигации с клавиатуры"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Устанавливаем фокус на поле логина
        window.login_input.setFocus()
        
        # Нажимаем Tab для перехода к следующему полю
        qtbot.keyClick(window.login_input, Qt.Key_Tab)
        assert window.password_input.hasFocus()
        
        qtbot.keyClick(window.password_input, Qt.Key_Tab)
        assert window.role_combo.hasFocus()
        
        qtbot.keyClick(window.role_combo, Qt.Key_Tab)
        assert window.login_button.hasFocus()
    
    def test_enter_key_triggers_login(self, qtbot, mock_db):
        """Тест что клавиша Enter вызывает вход"""
        window = LoginWindow()
        window.db = mock_db
        qtbot.addWidget(window)
        
        # Заполняем форму
        window.login_input.setText("test_user")
        window.password_input.setText("test_pass")
        
        # Мокаем метод login
        with patch.object(window, 'login') as mock_login:
            # Нажимаем Enter в поле пароля
            qtbot.keyClick(window.password_input, Qt.Key_Return)
            
            # Проверяем что метод login был вызван
            mock_login.assert_called_once()