from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QGroupBox, QTextEdit, QTabWidget,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont


class StudentWindow(QWidget):
    def __init__(self, user, db):
        super().__init__()
        self.user = user
        self.db = db
        self.init_ui()
        self.load_grades()

    def init_ui(self):
        self.setWindowTitle(f'Личный кабинет студента - {self.user.full_name}')
        self.setGeometry(100, 100, 1100, 700)

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
        <b>Специальность:</b> {self.user.specialty or "Не указана"}<br>
        <b>Группа:</b> {self.user.group_name or "Не указана"}<br>
        <b>ФИО:</b> {self.user.full_name}
        '''
        info_label = QLabel(info_text)
        info_label.setStyleSheet('font-size: 14px;')
        info_label.setTextFormat(Qt.RichText)
        info_layout.addWidget(info_label)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Статистика
        stats_group = QGroupBox('Статистика успеваемости')
        stats_layout = QHBoxLayout()
        
        # Средний балл
        avg_score = self.calculate_average_score()
        avg_label = QLabel(f'<b>Общий средний балл:</b> {avg_score:.2f}')
        avg_label.setStyleSheet('font-size: 16px; color: #27ae60;')
        avg_label.setTextFormat(Qt.RichText)
        stats_layout.addWidget(avg_label)
        
        # Количество оценок
        grades_count = self.get_grades_count()
        count_label = QLabel(f'<b>Всего оценок:</b> {grades_count}')
        count_label.setStyleSheet('font-size: 16px; color: #3498db;')
        count_label.setTextFormat(Qt.RichText)
        stats_layout.addWidget(count_label)
        
        # Процент освоения ФГОС
        fgos_percentage = self.calculate_fgos_percentage()
        fgos_label = QLabel(f'<b>Освоение ФГОС:</b> {fgos_percentage:.1f}%')
        fgos_label.setStyleSheet('font-size: 16px; color: #9b59b6;')
        fgos_label.setTextFormat(Qt.RichText)
        stats_layout.addWidget(fgos_label)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # Вкладки для отображения оценок
        self.tab_widget = QTabWidget()
        
        # Вкладка с таблицей оценок
        self.table_tab = QWidget()
        table_layout = QVBoxLayout()
        
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(9)
        self.grades_table.setHorizontalHeaderLabels([
            'Предмет', 'Компетенция', 'Тип', 'Оценка', 'Процент', 
            'Индикаторы освоения', 'Комментарий', 'Дата', 'Преподаватель'
        ])
        self.grades_table.horizontalHeader().setStretchLastSection(True)
        self.grades_table.setAlternatingRowColors(True)
        self.grades_table.setSortingEnabled(True)
        
        table_layout.addWidget(self.grades_table)
        self.table_tab.setLayout(table_layout)
        self.tab_widget.addTab(self.table_tab, "Таблица оценок")
        
        # Вкладка с детальной информацией
        self.detail_tab = QWidget()
        detail_layout = QVBoxLayout()
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setStyleSheet('font-size: 12px;')
        detail_layout.addWidget(self.detail_text)
        
        self.detail_tab.setLayout(detail_layout)
        self.tab_widget.addTab(self.detail_tab, "Детальная информация")
        
        main_layout.addWidget(self.tab_widget)

        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton('Обновить данные')
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
        
        self.export_button = QPushButton('Экспорт в PDF')
        self.export_button.clicked.connect(self.export_to_pdf)
        self.export_button.setStyleSheet('''
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px 20px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
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
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addWidget(self.logout_button)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
        
        # Подключаем выбор строки в таблице
        self.grades_table.itemSelectionChanged.connect(self.show_grade_details)

    def load_grades(self):
        """Загрузка оценок студента с деталями по ФГОС"""
        grades = self.db.get_student_grades_with_details(self.user.id)
        
        self.grades_table.setRowCount(len(grades))
        
        for row, grade in enumerate(grades):
            grade_id, subject, competency_code, competency_name, grade_value, percentage, comment, date, teacher_name, indicators = grade
            
            # Определяем тип компетенции по коду
            if competency_code.startswith('ПК'):
                comp_type = 'Профессиональная'
            elif competency_code.startswith('ОПК'):
                comp_type = 'Общепрофессиональная'
            elif competency_code.startswith('УК'):
                comp_type = 'Универсальная'
            else:
                comp_type = 'Другая'
            
            # Заполняем таблицу
            self.grades_table.setItem(row, 0, QTableWidgetItem(subject))
            self.grades_table.setItem(row, 1, QTableWidgetItem(f"{competency_code}: {competency_name[:30]}..."))
            self.grades_table.setItem(row, 2, QTableWidgetItem(comp_type))
            
            # Оценка с цветом
            grade_item = QTableWidgetItem(str(grade_value))
            grade_item.setBackground(self.get_grade_color(grade_value))
            grade_item.setData(Qt.UserRole, grade_id)  # Сохраняем ID для деталей
            self.grades_table.setItem(row, 3, grade_item)
            
            # Процент освоения
            percentage_item = QTableWidgetItem(f'{percentage:.1f}%')
            self.grades_table.setItem(row, 4, percentage_item)
            
            # Индикаторы
            indicators_item = QTableWidgetItem(indicators[:100] + '...' if len(indicators) > 100 else indicators)
            self.grades_table.setItem(row, 5, indicators_item)
            
            # Комментарий
            comment_item = QTableWidgetItem(comment[:100] + '...' if len(comment) > 100 else comment)
            self.grades_table.setItem(row, 6, comment_item)
            
            # Дата
            self.grades_table.setItem(row, 7, QTableWidgetItem(date))
            
            # Преподаватель
            self.grades_table.setItem(row, 8, QTableWidgetItem(teacher_name))
        
        self.grades_table.resizeColumnsToContents()
        
        # Обновляем статистику
        self.update_statistics()

    def show_grade_details(self):
        """Показ детальной информации о выбранной оценке"""
        selected_items = self.grades_table.selectedItems()
        if not selected_items:
            return
        
        current_row = selected_items[0].row()
        grade_id_item = self.grades_table.item(current_row, 3)
        if not grade_id_item:
            return
        
        grade_id = grade_id_item.data(Qt.UserRole)
        
        # Получаем полную информацию об оценке
        query = """
        SELECT g.id, s.name as subject, fc.code as competency_code, fc.name as competency_name,
               fc.description as competency_desc, fc.type as competency_type,
               g.grade_value, g.percentage, g.comment, g.date, u.full_name as teacher_name
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        JOIN fgos_competencies fc ON g.competency_id = fc.id
        JOIN users u ON g.teacher_id = u.id
        WHERE g.id = ?
        """
        
        grade_info = self.db.fetch_one(query, (grade_id,))
        if not grade_info:
            return
        
        # Получаем индикаторы для этой оценки
        indicator_query = """
        SELECT fi.code, fi.description, fi.weight
        FROM grade_indicators gi
        JOIN fgos_indicators fi ON gi.indicator_id = fi.id
        WHERE gi.grade_id = ?
        ORDER BY fi.code
        """
        
        indicators = self.db.fetch_all(indicator_query, (grade_id,))
        
        # Формируем текст для отображения
        detail_text = f"""
        <h2>Детальная информация об оценке</h2>
        <hr>
        
        <h3>Основная информация</h3>
        <b>Предмет:</b> {grade_info[1]}<br>
        <b>Компетенция ФГОС:</b> {grade_info[2]} - {grade_info[3]}<br>
        <b>Тип компетенции:</b> {grade_info[5]}<br>
        <b>Описание компетенции:</b> {grade_info[4]}<br>
        <b>Оценка:</b> <span style='color:{self.get_grade_color(grade_info[6]).name()};font-weight:bold;'>{grade_info[6]}</span><br>
        <b>Процент освоения:</b> {grade_info[7]:.1f}%<br>
        <b>Дата выставления:</b> {grade_info[9]}<br>
        <b>Преподаватель:</b> {grade_info[10]}<br>
        
        <h3>Освоенные индикаторы</h3>
        <ul>
        """
        
        for indicator_code, indicator_desc, weight in indicators:
            detail_text += f"<li><b>{indicator_code}:</b> {indicator_desc} (вес: {weight})</li>"
        
        detail_text += f"""
        </ul>
        <b>Всего освоено индикаторов:</b> {len(indicators)}<br>
        
        <h3>Комментарий преподавателя</h3>
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
        {grade_info[8]}
        </div>
        
        <h3>Интерпретация оценки</h3>
        {self.get_grade_interpretation(grade_info[6], grade_info[7])}
        """
        
        self.detail_text.setHtml(detail_text)

    def get_grade_interpretation(self, grade_value, percentage):
        """Получение интерпретации оценки"""
        if grade_value == 5:
            return """
            <div style='background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px;'>
            <b>Высокий уровень освоения (86-100%)</b><br>
            Студент демонстрирует полное понимание компетенции, способен творчески применять знания 
            в новых ситуациях, проявляет инициативу и самостоятельность.
            </div>
            """
        elif grade_value == 4:
            return """
            <div style='background-color: #d1ecf1; color: #0c5460; padding: 10px; border-radius: 5px;'>
            <b>Повышенный уровень освоения (67-85%)</b><br>
            Студент уверенно применяет компетенцию в типовых ситуациях, понимает основные принципы,
            но может испытывать затруднения в нестандартных условиях.
            </div>
            """
        elif grade_value == 3:
            return """
            <div style='background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px;'>
            <b>Базовый уровень освоения (48-66%)</b><br>
            Студент освоил основные элементы компетенции, но требуется дополнительная практика 
            и поддержка для уверенного применения.
            </div>
            """
        else:
            return """
            <div style='background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px;'>
            <b>Компетенция не сформирована (0-47%)</b><br>
            Требуется дополнительное обучение и практика. Рекомендуется индивидуальная работа 
            с преподавателем и дополнительные задания.
            </div>
            """

    def calculate_average_score(self):
        """Расчет среднего балла"""
        query = "SELECT AVG(grade_value) FROM grades WHERE student_id = ?"
        result = self.db.fetch_one(query, (self.user.id,))
        return result[0] if result and result[0] is not None else 0.0

    def get_grades_count(self):
        """Получение количества оценок"""
        query = "SELECT COUNT(*) FROM grades WHERE student_id = ?"
        result = self.db.fetch_one(query, (self.user.id,))
        return result[0] if result else 0

    def calculate_fgos_percentage(self):
        """Расчет общего процента освоения ФГОС"""
        query = "SELECT AVG(percentage) FROM grades WHERE student_id = ?"
        result = self.db.fetch_one(query, (self.user.id,))
        return result[0] if result and result[0] is not None else 0.0

    def update_statistics(self):
        """Обновление статистики"""
        avg_score = self.calculate_average_score()
        grades_count = self.get_grades_count()
        fgos_percentage = self.calculate_fgos_percentage()
        
        # Находим и обновляем labels в stats_group
        for child in self.findChildren(QLabel):
            if 'Общий средний балл' in child.text():
                child.setText(f'<b>Общий средний балл:</b> {avg_score:.2f}')
            elif 'Всего оценок' in child.text():
                child.setText(f'<b>Всего оценок:</b> {grades_count}')
            elif 'Освоение ФГОС' in child.text():
                child.setText(f'<b>Освоение ФГОС:</b> {fgos_percentage:.1f}%')

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

    def export_to_pdf(self):
        """Экспорт оценок в PDF"""
        QMessageBox.information(self, 'Экспорт', 
            'Функция экспорта в PDF будет реализована в следующей версии.\n'
            'Сейчас вы можете просмотреть детальную информацию во вкладке "Детальная информация".')