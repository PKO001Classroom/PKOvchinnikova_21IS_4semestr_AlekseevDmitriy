from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QGroupBox, QComboBox, QLineEdit,
    QTextEdit, QDateEdit, QFormLayout
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor
import sqlite3


class TeacherWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.init_ui()
        self.load_students()
        self.load_subjects()

    def init_ui(self):
        self.setWindowTitle(f'Панель преподавателя - {self.user.full_name}')
        self.setGeometry(100, 100, 1000, 700)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel(f'Преподаватель: {self.user.full_name}')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #2c3e50;')
        main_layout.addWidget(title_label)

        # Форма выставления оценки
        form_group = QGroupBox('Выставление оценки')
        form_layout = QFormLayout()

        # Студент
        self.student_combo = QComboBox()
        form_layout.addRow('Студент:', self.student_combo)

        # Предмет
        self.subject_combo = QComboBox()
        form_layout.addRow('Предмет:', self.subject_combo)

        # Оценка
        self.grade_combo = QComboBox()
        self.grade_combo.addItems(['5', '4', '3', '2'])
        form_layout.addRow('Оценка:', self.grade_combo)

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow('Дата:', self.date_edit)

        # Комментарий
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText('Введите комментарий (минимум 100 символов с указанием кода компетенции)')
        self.comment_edit.setMaximumHeight(100)
        form_layout.addRow('Комментарий:', self.comment_edit)

        # Кнопка добавления
        self.add_grade_button = QPushButton('Добавить оценку')
        self.add_grade_button.clicked.connect(self.add_grade)
        self.add_grade_button.setStyleSheet('''
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        ''')
        form_layout.addRow('', self.add_grade_button)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # Таблица оценок
        grades_group = QGroupBox('Журнал оценок')
        grades_layout = QVBoxLayout()
        
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(7)
        self.grades_table.setHorizontalHeaderLabels([
            'Студент', 'Предмет', 'Оценка', 'Комментарий', 'Дата', 'Специальность', 'Группа'
        ])
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.setAlternatingRowColors(True)
        
        grades_layout.addWidget(self.grades_table)
        grades_group.setLayout(grades_layout)
        main_layout.addWidget(grades_group)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton('Обновить журнал')
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

    def load_students(self):
        """Загрузка списка студентов"""
        query = "SELECT id, full_name FROM users WHERE role = 'student'"
        students = self.db.fetch_all(query)
        
        self.student_combo.clear()
        for student_id, full_name in students:
            self.student_combo.addItem(full_name, student_id)

    def load_subjects(self):
        """Загрузка списка предметов"""
        query = "SELECT id, name FROM subjects"
        subjects = self.db.fetch_all(query)
        
        self.subject_combo.clear()
        for subject_id, name in subjects:
            self.subject_combo.addItem(name, subject_id)

    def load_grades(self):
        """Загрузка всех оценок"""
        query = '''
        SELECT u.full_name, s.name, g.grade_value, g.comment, g.date, u.specialty, u.group_name
        FROM grades g
        JOIN users u ON g.student_id = u.id
        JOIN subjects s ON g.subject_id = s.id
        WHERE g.teacher_id = ?
        ORDER BY g.date DESC
        '''
        grades = self.db.fetch_all(query, (self.user.id,))
        
        self.grades_table.setRowCount(len(grades))
        
        for row, grade in enumerate(grades):
            student, subject, grade_value, comment, date, specialty, group_name = grade
            
            # Цвет оценки
            color = self.get_grade_color(grade_value)
            
            # Заполнение таблицы
            self.grades_table.setItem(row, 0, QTableWidgetItem(student))
            self.grades_table.setItem(row, 1, QTableWidgetItem(subject))
            
            grade_item = QTableWidgetItem(str(grade_value))
            grade_item.setBackground(color)
            self.grades_table.setItem(row, 2, grade_item)
            
            self.grades_table.setItem(row, 3, QTableWidgetItem(comment))
            self.grades_table.setItem(row, 4, QTableWidgetItem(date))
            self.grades_table.setItem(row, 5, QTableWidgetItem(specialty or ''))
            self.grades_table.setItem(row, 6, QTableWidgetItem(group_name or ''))

        self.grades_table.resizeColumnsToContents()

    def add_grade(self):
        """Добавление новой оценки"""
        student_id = self.student_combo.currentData()
        subject_id = self.subject_combo.currentData()
        grade_value = int(self.grade_combo.currentText())
        date = self.date_edit.date().toString('yyyy-MM-dd')
        comment = self.comment_edit.toPlainText().strip()

        # Валидация
        if not student_id or not subject_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите студента и предмет')
            return

        if len(comment) < 100:
            QMessageBox.warning(self, 'Ошибка', 'Комментарий должен содержать минимум 100 символов')
            return

        if 'ПК' not in comment and 'ОПК' not in comment:
            QMessageBox.warning(self, 'Предупреждение', 'Рекомендуется указать код компетенции (ПК или ОПК) в комментарии')

        # Добавление в базу данных
        try:
            query = '''
            INSERT INTO grades (student_id, teacher_id, subject_id, grade_value, comment, date)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            self.db.execute_query(query, (student_id, self.user.id, subject_id, grade_value, comment, date))
            
            QMessageBox.information(self, 'Успех', 'Оценка успешно добавлена')
            
            # Очистка формы
            self.comment_edit.clear()
            self.date_edit.setDate(QDate.currentDate())
            
            # Обновление таблицы
            self.load_grades()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при добавлении оценки: {str(e)}')

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