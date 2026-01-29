from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class StudentWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.init_ui()
        self.load_grades()

    def init_ui(self):
        self.setWindowTitle(f'Личный кабинет студента - {self.user.full_name}')
        self.setGeometry(100, 100, 900, 600)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel(f'Студент: {self.user.full_name}')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #2c3e50;')
        main_layout.addWidget(title_label)

        # Информация о студенте
        info_group = QGroupBox('Информация о студенте')
        info_layout = QHBoxLayout()
        
        info_text = f'''
        Специальность: {self.user.specialty or "Не указана"}
        Группа: {self.user.group_name or "Не указана"}
        '''
        info_label = QLabel(info_text)
        info_label.setStyleSheet('font-size: 14px;')
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Средний балл
        avg_score = self.calculate_average_score()
        avg_group = QGroupBox('Средний балл')
        avg_layout = QHBoxLayout()
        
        avg_label = QLabel(f'Общий средний балл: {avg_score:.2f}')
        avg_label.setStyleSheet('font-size: 16px; font-weight: bold; color: #27ae60;')
        avg_layout.addWidget(avg_label)
        
        avg_group.setLayout(avg_layout)
        main_layout.addWidget(avg_group)

        # Таблица оценок
        grades_group = QGroupBox('Оценки')
        grades_layout = QVBoxLayout()
        
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(6)
        self.grades_table.setHorizontalHeaderLabels([
            'Предмет', 'Код', 'Оценка', 'Комментарий', 'Дата', 'Преподаватель'
        ])
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.setAlternatingRowColors(True)
        
        grades_layout.addWidget(self.grades_table)
        grades_group.setLayout(grades_layout)
        main_layout.addWidget(grades_group)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton('Обновить')
        self.refresh_button.clicked.connect(self.load_grades)
        self.refresh_button.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        
        self.logout_button = QPushButton('Выйти')
        self.logout_button.clicked.connect(self.close)
        self.logout_button.setStyleSheet('''
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        ''')
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.logout_button)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def load_grades(self):
        """Загрузка оценок студента"""
        query = '''
        SELECT s.name, s.code, g.grade_value, g.comment, g.date, u.full_name 
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        JOIN users u ON g.teacher_id = u.id
        WHERE g.student_id = ?
        ORDER BY g.date DESC
        '''
        grades = self.db.fetch_all(query, (self.user.id,))
        
        self.grades_table.setRowCount(len(grades))
        
        for row, grade in enumerate(grades):
            subject, code, grade_value, comment, date, teacher = grade
            
            # Цвет оценки
            color = self.get_grade_color(grade_value)
            
            # Заполнение таблицы
            self.grades_table.setItem(row, 0, QTableWidgetItem(subject))
            self.grades_table.setItem(row, 1, QTableWidgetItem(code))
            
            grade_item = QTableWidgetItem(str(grade_value))
            grade_item.setBackground(color)
            self.grades_table.setItem(row, 2, grade_item)
            
            self.grades_table.setItem(row, 3, QTableWidgetItem(comment))
            self.grades_table.setItem(row, 4, QTableWidgetItem(date))
            self.grades_table.setItem(row, 5, QTableWidgetItem(teacher))

        self.grades_table.resizeColumnsToContents()

    def calculate_average_score(self):
        """Расчет среднего балла"""
        query = '''
        SELECT AVG(grade_value) 
        FROM grades 
        WHERE student_id = ?
        '''
        result = self.db.fetch_one(query, (self.user.id,))
        return result[0] if result and result[0] is not None else 0.0

    def get_grade_color(self, grade_value):
        """Получение цвета в зависимости от оценки"""
        if grade_value == 5:
            return QColor(144, 238, 144)  # Светло-зеленый
        elif grade_value == 4:
            return QColor(173, 216, 230)  # Светло-голубой
        elif grade_value == 3:
            return QColor(255, 255, 153)  # Светло-желтый
        else:
            return QColor(255, 182, 193)  # Светло-розовый