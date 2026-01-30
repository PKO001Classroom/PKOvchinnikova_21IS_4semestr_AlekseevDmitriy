from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QGroupBox, QComboBox, QLineEdit,
    QTextEdit, QDateEdit, QFormLayout, QCheckBox,
    QScrollArea, QFrame, QGridLayout, QButtonGroup,
    QRadioButton, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
import sqlite3
from datetime import datetime


class TeacherWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.selected_indicators = set()  # Множество выбранных индикаторов
        self.current_competency_id = None
        self.init_ui()
        self.load_students()
        self.load_subjects()

    def init_ui(self):
        self.setWindowTitle(f'Панель преподавателя - {self.user.full_name}')
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title_label = QLabel(f'Преподаватель: {self.user.full_name}')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 20px; font-weight: bold; color: #2c3e50;')
        main_layout.addWidget(title_label)

        # Основной контейнер с двумя колонками
        container = QHBoxLayout()
        
        # Левая колонка - форма выставления оценки
        left_column = QVBoxLayout()
        
        # Форма выставления оценки
        form_group = QGroupBox('Выставление оценки по ФГОС')
        form_layout = QVBoxLayout()

        # Студент
        student_layout = QHBoxLayout()
        student_layout.addWidget(QLabel('Студент:'))
        self.student_combo = QComboBox()
        student_layout.addWidget(self.student_combo)
        form_layout.addLayout(student_layout)

        # Предмет
        subject_layout = QHBoxLayout()
        subject_layout.addWidget(QLabel('Предмет:'))
        self.subject_combo = QComboBox()
        self.subject_combo.currentIndexChanged.connect(self.load_competencies)
        subject_layout.addWidget(self.subject_combo)
        form_layout.addLayout(subject_layout)

        # Компетенция ФГОС
        competency_layout = QHBoxLayout()
        competency_layout.addWidget(QLabel('Компетенция ФГОС:'))
        self.competency_combo = QComboBox()
        self.competency_combo.currentIndexChanged.connect(self.load_indicators)
        competency_layout.addWidget(self.competency_combo)
        form_layout.addLayout(competency_layout)

        # Область для индикаторов
        indicators_group = QGroupBox('Индикаторы освоения')
        indicators_layout = QVBoxLayout()
        
        # Scroll area для индикаторов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(200)
        
        self.indicators_widget = QWidget()
        self.indicators_layout = QVBoxLayout(self.indicators_widget)
        scroll.setWidget(self.indicators_widget)
        
        indicators_layout.addWidget(scroll)
        indicators_group.setLayout(indicators_layout)
        form_layout.addWidget(indicators_group)

        # Прогресс и оценка
        progress_layout = QHBoxLayout()
        
        self.progress_label = QLabel('Выберите индикаторы освоения')
        self.progress_label.setStyleSheet('font-weight: bold; color: #3498db;')
        progress_layout.addWidget(self.progress_label)
        
        self.grade_label = QLabel('Оценка: --')
        self.grade_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        progress_layout.addWidget(self.grade_label)
        
        form_layout.addLayout(progress_layout)

        # Дата
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('Дата:'))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        date_layout.addWidget(self.date_edit)
        form_layout.addLayout(date_layout)

        # Комментарий
        comment_layout = QVBoxLayout()
        comment_layout.addWidget(QLabel('Комментарий (обоснование оценки):'))
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText(
            'Опишите достижения студента по выбранным индикаторам. '
            'Минимум 100 символов. Укажите рекомендации для дальнейшего развития.'
        )
        self.comment_edit.setMaximumHeight(100)
        comment_layout.addWidget(self.comment_edit)
        form_layout.addLayout(comment_layout)

        # Кнопка добавления оценки
        self.add_grade_button = QPushButton('Выставить оценку')
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
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        ''')
        form_layout.addWidget(self.add_grade_button)

        form_group.setLayout(form_layout)
        left_column.addWidget(form_group)
        
        # Правая колонка - журнал оценок
        right_column = QVBoxLayout()
        
        grades_group = QGroupBox('Журнал оценок')
        grades_layout = QVBoxLayout()
        
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(8)
        self.grades_table.setHorizontalHeaderLabels([
            'Студент', 'Предмет', 'Компетенция', 'Оценка', 'Индикаторы', 'Комментарий', 'Дата', 'Процент'
        ])
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.setSortingEnabled(True)
        
        grades_layout.addWidget(self.grades_table)
        grades_group.setLayout(grades_layout)
        right_column.addWidget(grades_group)
        
        # Кнопки управления журналом
        journal_buttons = QHBoxLayout()
        
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
        
        journal_buttons.addWidget(self.refresh_button)
        journal_buttons.addWidget(self.logout_button)
        right_column.addLayout(journal_buttons)

        # Добавляем колонки в контейнер
        container.addLayout(left_column, 40)
        container.addLayout(right_column, 60)
        
        main_layout.addLayout(container)
        self.setLayout(main_layout)

        # Загружаем начальные данные
        self.load_grades()

    def load_students(self):
        """Загрузка списка студентов"""
        query = "SELECT id, full_name FROM users WHERE role = 'student' ORDER BY full_name"
        students = self.db.fetch_all(query)
        
        self.student_combo.clear()
        for student_id, full_name in students:
            self.student_combo.addItem(full_name, student_id)

    def load_subjects(self):
        """Загрузка списка предметов"""
        query = "SELECT id, name FROM subjects WHERE teacher_id = ? OR teacher_id IS NULL ORDER BY name"
        subjects = self.db.fetch_all(query, (self.user.id,))
        
        self.subject_combo.clear()
        for subject_id, name in subjects:
            self.subject_combo.addItem(name, subject_id)
        
        if self.subject_combo.count() > 0:
            self.load_competencies()

    def load_competencies(self):
        """Загрузка компетенций ФГОС для выбранного предмета"""
        subject_id = self.subject_combo.currentData()
        if not subject_id:
            return
        
        competencies = self.db.get_competencies_by_subject(subject_id)
        
        self.competency_combo.clear()
        for competency_id, code, name, type_ in competencies:
            display_text = f"{code} ({type_}): {name[:50]}..."
            self.competency_combo.addItem(display_text, competency_id)
        
        if self.competency_combo.count() > 0:
            self.load_indicators()

    def load_indicators(self):
        """Загрузка индикаторов для выбранной компетенции"""
        # Очищаем предыдущие индикаторы
        for i in reversed(range(self.indicators_layout.count())):
            widget = self.indicators_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        self.selected_indicators.clear()
        self.current_competency_id = self.competency_combo.currentData()
        
        if not self.current_competency_id:
            return
        
        # Получаем индикаторы
        indicators = self.db.get_indicators_by_competency(self.current_competency_id)
        
        for indicator_id, code, description, weight, max_score in indicators:
            checkbox = QCheckBox(f"{code}: {description}")
            checkbox.setProperty('indicator_id', indicator_id)
            checkbox.stateChanged.connect(self.on_indicator_changed)
            self.indicators_layout.addWidget(checkbox)
        
        # Добавляем растягивающий элемент
        self.indicators_layout.addStretch()
        
        self.update_progress()

    def on_indicator_changed(self, state):
        """Обработка изменения состояния индикатора"""
        checkbox = self.sender()
        indicator_id = checkbox.property('indicator_id')
        
        if state == Qt.Checked:
            self.selected_indicators.add(indicator_id)
        else:
            self.selected_indicators.discard(indicator_id)
        
        self.update_progress()

    def update_progress(self):
        """Обновление прогресса и расчет оценки"""
        if not self.current_competency_id:
            self.progress_label.setText('Выберите компетенцию')
            self.grade_label.setText('Оценка: --')
            self.add_grade_button.setEnabled(False)
            return
        
        grade_value, percentage = self.db.calculate_grade_from_indicators(
            list(self.selected_indicators), self.current_competency_id
        )
        
        # Получаем все индикаторы для подсчета
        indicators = self.db.get_indicators_by_competency(self.current_competency_id)
        total_indicators = len(indicators)
        selected_count = len(self.selected_indicators)
        
        # Получаем требования для этой компетенции
        requirements = self.get_requirements_text(total_indicators)
        
        self.progress_label.setText(
            f'Выбрано индикаторов: {selected_count}/{total_indicators} ({percentage:.1f}%) | {requirements}'
        )
        
        # Устанавливаем текст оценки с цветом
        grade_text = f'Оценка: {grade_value}'
        grade_description = self.get_grade_description(grade_value)
        
        self.grade_label.setText(f'{grade_text} - {grade_description}')
        
        # Меняем цвет в зависимости от оценки
        color = self.get_grade_color(grade_value)
        self.grade_label.setStyleSheet(f'font-size: 16px; font-weight: bold; color: {color.name()};')
        
        # Активируем кнопку если есть выбранные индикаторы
        self.add_grade_button.setEnabled(selected_count > 0)

    def get_requirements_text(self, total_indicators):
        """Получение текста требований"""
        if total_indicators >= 8:
            return "Требования: 5(6-8), 4(5), 3(4), 2(0-3)"
        elif total_indicators >= 6:
            return "Требования: 5(5-6), 4(4), 3(3), 2(0-2)"
        else:
            return "Требования: 5(86-100%), 4(67-85%), 3(48-66%), 2(0-47%)"

    def get_grade_description(self, grade_value):
        """Получение описания оценки"""
        descriptions = {
            5: 'Высокий уровень (75-100%)',
            4: 'Повышенный уровень (60-74%)',
            3: 'Базовый уровень (50-59%)',
            2: 'Не сформировано (0-49%)'
        }
        return descriptions.get(grade_value, 'Не определена')

    def add_grade(self):
        """Добавление новой оценки"""
        # Проверка выбора студента
        student_id = self.student_combo.currentData()
        if not student_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите студента')
            return
        
        # Проверка выбора предмета
        subject_id = self.subject_combo.currentData()
        if not subject_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите предмет')
            return
        
        # Проверка выбора компетенции
        competency_id = self.competency_combo.currentData()
        if not competency_id:
            QMessageBox.warning(self, 'Ошибка', 'Выберите компетенцию ФГОС')
            return
        
        # Проверка выбора индикаторов
        if not self.selected_indicators:
            QMessageBox.warning(self, 'Ошибка', 'Выберите хотя бы один индикатор освоения')
            return
        
        # Проверка комментария
        comment = self.comment_edit.toPlainText().strip()
        if len(comment) < 100:
            QMessageBox.warning(self, 'Ошибка', 'Комментарий должен содержать минимум 100 символов')
            return
        
        # Расчет оценки
        grade_value, percentage = self.db.calculate_grade_from_indicators(
            list(self.selected_indicators), competency_id
        )
        
        # Подготовка данных
        grade_data = {
            'student_id': student_id,
            'teacher_id': self.user.id,
            'subject_id': subject_id,
            'competency_id': competency_id,
            'grade_value': grade_value,
            'percentage': percentage,
            'comment': comment,
            'date': self.date_edit.date().toString('yyyy-MM-dd')
        }
        
        # Сохранение в базу данных
        try:
            success = self.db.add_grade_with_indicators(grade_data, list(self.selected_indicators))
            if success:
                QMessageBox.information(self, 'Успех', 'Оценка успешно выставлена!')
                
                # Очистка формы
                self.comment_edit.clear()
                self.date_edit.setDate(QDate.currentDate())
                self.selected_indicators.clear()
                
                # Сброс чекбоксов
                for i in range(self.indicators_layout.count()):
                    widget = self.indicators_layout.itemAt(i).widget()
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(False)
                
                self.update_progress()
                self.load_grades()
            else:
                QMessageBox.critical(self, 'Ошибка', 'Ошибка при сохранении оценки')
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка базы данных: {str(e)}')

    def load_grades(self):
        """Загрузка всех оценок"""
        query = """
        SELECT g.id, u.full_name, s.name, fc.code, 
               g.grade_value, g.comment, g.date, g.percentage
        FROM grades g
        JOIN users u ON g.student_id = u.id
        JOIN subjects s ON g.subject_id = s.id
        JOIN fgos_competencies fc ON g.competency_id = fc.id
        WHERE g.teacher_id = ?
        ORDER BY g.date DESC
        """
        
        grades = self.db.fetch_all(query, (self.user.id,))
        
        self.grades_table.setRowCount(len(grades))
        
        for row, grade in enumerate(grades):
            grade_id, student_name, subject_name, competency_code, grade_value, comment, date, percentage = grade
            
            # Получаем индикаторы для этой оценки
            indicator_query = """
            SELECT fi.description 
            FROM grade_indicators gi
            JOIN fgos_indicators fi ON gi.indicator_id = fi.id
            WHERE gi.grade_id = ?
            """
            indicators = self.db.fetch_all(indicator_query, (grade_id,))
            indicator_text = '; '.join([ind[0] for ind in indicators])
            
            # Заполняем таблицу
            self.grades_table.setItem(row, 0, QTableWidgetItem(student_name))
            self.grades_table.setItem(row, 1, QTableWidgetItem(subject_name))
            self.grades_table.setItem(row, 2, QTableWidgetItem(competency_code))
            
            grade_item = QTableWidgetItem(str(grade_value))
            grade_item.setBackground(self.get_grade_color(grade_value))
            self.grades_table.setItem(row, 3, grade_item)
            
            self.grades_table.setItem(row, 4, QTableWidgetItem(indicator_text[:100] + '...' if len(indicator_text) > 100 else indicator_text))
            self.grades_table.setItem(row, 5, QTableWidgetItem(comment[:100] + '...' if len(comment) > 100 else comment))
            self.grades_table.setItem(row, 6, QTableWidgetItem(date))
            
            percentage_item = QTableWidgetItem(f'{percentage:.1f}%')
            self.grades_table.setItem(row, 7, percentage_item)
        
        self.grades_table.resizeColumnsToContents()

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