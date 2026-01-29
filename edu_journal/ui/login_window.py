from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt


class LoginWindow(QWidget):
    def __init__(self, db, on_login_success):
        super().__init__()
        self.db = db
        self.on_login_success = on_login_success
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Вход в систему - Учебный журнал')
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # Заголовок
        title_label = QLabel('Вход в систему')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title_label)

        # Поле логина
        login_layout = QHBoxLayout()
        login_label = QLabel('Логин:')
        login_label.setFixedWidth(80)
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText('Введите логин')
        login_layout.addWidget(login_label)
        login_layout.addWidget(self.login_input)
        layout.addLayout(login_layout)

        # Поле пароля
        password_layout = QHBoxLayout()
        password_label = QLabel('Пароль:')
        password_label.setFixedWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Роль (для тестирования)
        role_layout = QHBoxLayout()
        role_label = QLabel('Роль:')
        role_label.setFixedWidth(80)
        self.role_combo = QComboBox()
        self.role_combo.addItems(['teacher', 'student'])
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.login)
        self.login_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')
        
        self.exit_button = QPushButton('Выход')
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        ''')

        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.exit_button)
        layout.addLayout(buttons_layout)

        # Тестовые данные
        test_label = QLabel('Тестовые данные:\nУчитель: teacher1/123456\nСтудент: student1/123456')
        test_label.setStyleSheet('font-size: 10px; color: gray;')
        test_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(test_label)

        self.setLayout(layout)

    def login(self):
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()
        selected_role = self.role_combo.currentText()

        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Пожалуйста, заполните все поля')
            return

        # Поиск пользователя в базе данных
        query = "SELECT * FROM users WHERE username = ? AND password = ? AND role = ?"
        user_data = self.db.fetch_one(query, (username, password, selected_role))

        if user_data:
            from models import User
            self.current_user = User(*user_data)
            QMessageBox.information(self, 'Успех', f'Добро пожаловать, {self.current_user.full_name}!')
            self.hide()
            self.on_login_success(self.current_user)
        else:
            QMessageBox.critical(self, 'Ошибка', 'Неверный логин, пароль или роль')