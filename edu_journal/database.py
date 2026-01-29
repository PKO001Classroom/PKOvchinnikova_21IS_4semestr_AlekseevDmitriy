import sqlite3
from sqlite3 import Error
import os

class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            # Создаем папку data если ее нет
            if not os.path.exists('data'):
                os.makedirs('data')
            db_path = 'data/edu_journal.db'
        
        print(f"Используется база данных: {os.path.abspath(db_path)}")
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def create_connection(self):
        """Создание подключения к базе данных"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"✓ Подключение к базе данных установлено")
            return self.connection
        except Error as e:
            print(f"✗ Ошибка подключения к базе данных: {e}")
            print(f"Путь: {self.db_path}")
            # Пробуем создать базу в текущей директории
            try:
                self.db_path = 'edu_journal.db'
                self.connection = sqlite3.connect(self.db_path)
                print(f"✓ База данных создана в текущей папке: {self.db_path}")
                return self.connection
            except Error as e2:
                print(f"✗ Критическая ошибка: {e2}")
                return None

    def init_database(self):
        """Инициализация базы данных с тестовыми данными по ФГОС"""
        conn = self.create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                
                # Создание таблицы пользователей
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
                    full_name TEXT NOT NULL,
                    specialty TEXT,
                    group_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

                # Создание таблицы предметов
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT,
                    specialty TEXT,
                    teacher_id INTEGER REFERENCES users(id)
                )
                ''')

                # Создание таблицы компетенций ФГОС
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS fgos_competencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    specialty TEXT,
                    type TEXT CHECK(type IN ('ПК', 'ОПК', 'УК'))
                )
                ''')

                # Создание таблицы индикаторов освоения (пунктов ФГОС)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS fgos_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competency_id INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    description TEXT NOT NULL,
                    weight INTEGER DEFAULT 1,
                    max_score INTEGER DEFAULT 1,
                    FOREIGN KEY (competency_id) REFERENCES fgos_competencies(id)
                )
                ''')

                # Создание таблицы оценок с привязкой к индикаторам ФГОС
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    competency_id INTEGER NOT NULL,
                    
                    -- Данные по ФГОС
                    grade_value INTEGER NOT NULL CHECK(grade_value BETWEEN 2 AND 5),
                    percentage INTEGER NOT NULL CHECK(percentage BETWEEN 0 AND 100),
                    comment TEXT NOT NULL CHECK(LENGTH(comment) >= 100),
                    
                    -- Системные поля
                    date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (student_id) REFERENCES users(id),
                    FOREIGN KEY (teacher_id) REFERENCES users(id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(id),
                    FOREIGN KEY (competency_id) REFERENCES fgos_competencies(id)
                )
                ''')

                # Таблица для хранения выбранных индикаторов для каждой оценки
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS grade_indicators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    grade_id INTEGER NOT NULL,
                    indicator_id INTEGER NOT NULL,
                    score INTEGER NOT NULL DEFAULT 1,
                    FOREIGN KEY (grade_id) REFERENCES grades(id),
                    FOREIGN KEY (indicator_id) REFERENCES fgos_indicators(id)
                )
                ''')

                # Добавление тестовых пользователей
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    print("Добавление тестовых пользователей...")
                    test_users = [
                        ('teacher1', '123456', 'teacher', 'Иванов Иван Иванович', '15.02.01', 'Преподаватель'),
                        ('student1', '123456', 'student', 'Петров Петр Петрович', '15.02.01', 'Группа 101'),
                        ('student2', '123456', 'student', 'Сидорова Анна Сергеевна', '15.02.01', 'Группа 101'),
                    ]
                    cursor.executemany(
                        "INSERT INTO users (username, password, role, full_name, specialty, group_name) VALUES (?, ?, ?, ?, ?, ?)",
                        test_users
                    )

                # Добавление тестовых предметов
                cursor.execute("SELECT COUNT(*) FROM subjects")
                if cursor.fetchone()[0] == 0:
                    print("Добавление тестовых предметов...")
                    test_subjects = [
                        ('Математика', 'МАТ-101', '15.02.01', 1),
                        ('Программирование', 'ПРОГ-102', '15.02.01', 1),
                        ('Базы данных', 'БД-103', '15.02.01', 1),
                    ]
                    cursor.executemany(
                        "INSERT INTO subjects (name, code, specialty, teacher_id) VALUES (?, ?, ?, ?)",
                        test_subjects
                    )

                # Добавление компетенций ФГОС для специальности 15.02.01 (Автоматизация технологических процессов)
                cursor.execute("SELECT COUNT(*) FROM fgos_competencies")
                if cursor.fetchone()[0] == 0:
                    print("Добавление компетенций ФГОС...")
                    competencies = [
                        # Профессиональные компетенции (ПК)
                        ('ПК 1.1', 'Выполнять наладку, регулировку и проверку электрического и электромеханического оборудования', 
                         'Наладка и регулировка оборудования', '15.02.01', 'ПК'),
                        ('ПК 1.2', 'Осуществлять диагностирование и техническое обслуживание электрооборудования', 
                         'Диагностика и обслуживание', '15.02.01', 'ПК'),
                        ('ПК 2.1', 'Разрабатывать и оформлять конструкторскую и технологическую документацию', 
                         'Разработка документации', '15.02.01', 'ПК'),
                        ('ПК 2.2', 'Выполнять расчеты и конструирование деталей и узлов электрооборудования', 
                         'Расчеты и конструирование', '15.02.01', 'ПК'),
                        ('ПК 3.1', 'Контролировать и анализировать функционирование параметров оборудования', 
                         'Контроль параметров', '15.02.01', 'ПК'),
                        
                        # Общепрофессиональные компетенции (ОПК)
                        ('ОПК 1.1', 'Понимать сущность и социальную значимость своей будущей профессии', 
                         'Понимание профессии', '15.02.01', 'ОПК'),
                        ('ОПК 2.1', 'Организовывать собственную деятельность', 
                         'Организация деятельности', '15.02.01', 'ОПК'),
                        ('ОПК 3.1', 'Работать в коллективе и команде', 
                         'Работа в команде', '15.02.01', 'ОПК'),
                        ('ОПК 4.1', 'Осуществлять поиск и использование информации', 
                         'Работа с информацией', '15.02.01', 'ОПК'),
                        
                        # Универсальные компетенции (УК)
                        ('УК 1.1', 'Понимать и анализировать мировоззренческие проблемы', 
                         'Мировоззрение', '15.02.01', 'УК'),
                        ('УК 2.1', 'Использовать современные коммуникативные технологии', 
                         'Коммуникативные технологии', '15.02.01', 'УК'),
                        ('УК 3.1', 'Самостоятельно определять задачи профессионального развития', 
                         'Профессиональное развитие', '15.02.01', 'УК'),
                    ]
                    cursor.executemany(
                        "INSERT INTO fgos_competencies (code, name, description, specialty, type) VALUES (?, ?, ?, ?, ?)",
                        competencies
                    )

                # Добавление индикаторов освоения для каждой компетенции
                cursor.execute("SELECT COUNT(*) FROM fgos_indicators")
                if cursor.fetchone()[0] == 0:
                    print("Добавление индикаторов ФГОС...")
                    
                    # Получаем ID компетенций
                    cursor.execute("SELECT id, code FROM fgos_competencies")
                    competencies = {row[1]: row[0] for row in cursor.fetchall()}
                    
                    indicators = [
                        # Индикаторы для ПК 1.1
                        (competencies['ПК 1.1'], 'ПК 1.1.1', 'Выполнил наладку оборудования согласно инструкции', 1, 1),
                        (competencies['ПК 1.1'], 'ПК 1.1.2', 'Произвел регулировку параметров в заданных пределах', 1, 1),
                        (competencies['ПК 1.1'], 'ПК 1.1.3', 'Проверил работоспособность после наладки', 1, 1),
                        (competencies['ПК 1.1'], 'ПК 1.1.4', 'Выявил и устранил неисправности', 2, 1),
                        (competencies['ПК 1.1'], 'ПК 1.1.5', 'Документировал результаты наладки', 1, 1),
                        
                        # Индикаторы для ПК 1.2
                        (competencies['ПК 1.2'], 'ПК 1.2.1', 'Провел диагностику оборудования', 1, 1),
                        (competencies['ПК 1.2'], 'ПК 1.2.2', 'Выполнил техническое обслуживание по плану', 1, 1),
                        (competencies['ПК 1.2'], 'ПК 1.2.3', 'Определил изношенные детали', 1, 1),
                        (competencies['ПК 1.2'], 'ПК 1.2.4', 'Составил отчет о техническом состоянии', 2, 1),
                        
                        # Индикаторы для ПК 2.1
                        (competencies['ПК 2.1'], 'ПК 2.1.1', 'Разработал чертеж детали', 1, 1),
                        (competencies['ПК 2.1'], 'ПК 2.1.2', 'Оформил технологическую карту', 1, 1),
                        (competencies['ПК 2.1'], 'ПК 2.1.3', 'Соблюл требования ЕСКД', 2, 1),
                        (competencies['ПК 2.1'], 'ПК 2.1.4', 'Применил стандарты оформления', 1, 1),
                        
                        # Индикаторы для ОПК 2.1
                        (competencies['ОПК 2.1'], 'ОПК 2.1.1', 'Составил план работы', 1, 1),
                        (competencies['ОПК 2.1'], 'ОПК 2.1.2', 'Распределил время эффективно', 1, 1),
                        (competencies['ОПК 2.1'], 'ОПК 2.1.3', 'Выполнил работу в срок', 2, 1),
                        (competencies['ОПК 2.1'], 'ОПК 2.1.4', 'Проанализировал результаты', 1, 1),
                        
                        # Индикаторы для ОПК 3.1
                        (competencies['ОПК 3.1'], 'ОПК 3.1.1', 'Участвовал в обсуждении задачи', 1, 1),
                        (competencies['ОПК 3.1'], 'ОПК 3.1.2', 'Выполнил свою часть работы', 1, 1),
                        (competencies['ОПК 3.1'], 'ОПК 3.1.3', 'Помог другим членам команды', 2, 1),
                        (competencies['ОПК 3.1'], 'ОПК 3.1.4', 'Представил результаты команды', 1, 1),
                        
                        # Индикаторы для УК 3.1
                        (competencies['УК 3.1'], 'УК 3.1.1', 'Определил цели развития', 1, 1),
                        (competencies['УК 3.1'], 'УК 3.1.2', 'Составил план самообразования', 1, 1),
                        (competencies['УК 3.1'], 'УК 3.1.3', 'Изучил дополнительную литературу', 2, 1),
                        (competencies['УК 3.1'], 'УК 3.1.4', 'Применил новые знания на практике', 2, 1),
                    ]
                    
                    cursor.executemany(
                        "INSERT INTO fgos_indicators (competency_id, code, description, weight, max_score) VALUES (?, ?, ?, ?, ?)",
                        indicators
                    )

                # Добавление тестовых оценок
                cursor.execute("SELECT COUNT(*) FROM grades")
                if cursor.fetchone()[0] == 0:
                    print("Добавление тестовых оценок...")
                    
                    # Получаем ID для тестовых данных
                    cursor.execute("SELECT id FROM users WHERE username = 'student1'")
                    student_id = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT id FROM subjects WHERE name = 'Математика'")
                    subject_id = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT id FROM fgos_competencies WHERE code = 'ПК 1.1'")
                    competency_id = cursor.fetchone()[0]
                    
                    # Добавляем оценку
                    cursor.execute(
                        """INSERT INTO grades 
                        (student_id, teacher_id, subject_id, competency_id, grade_value, percentage, comment, date) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (student_id, 1, subject_id, competency_id, 5, 90, 
                         'Студент успешно освоил компетенцию ПК 1.1. Выполнил наладку оборудования, произвел регулировку параметров, проверил работоспособность. Продемонстрировал понимание принципов работы оборудования и способность устранять неисправности. Рекомендуется для участия в конкурсах профессионального мастерства.', 
                         '2024-01-15')
                    )
                    
                    # Получаем ID добавленной оценки
                    grade_id = cursor.lastrowid
                    
                    # Добавляем выбранные индикаторы для этой оценки
                    cursor.execute("SELECT id FROM fgos_indicators WHERE code IN ('ПК 1.1.1', 'ПК 1.1.2', 'ПК 1.1.3', 'ПК 1.1.4', 'ПК 1.1.5')")
                    indicator_ids = [row[0] for row in cursor.fetchall()]
                    
                    for indicator_id in indicator_ids:
                        cursor.execute(
                            "INSERT INTO grade_indicators (grade_id, indicator_id, score) VALUES (?, ?, ?)",
                            (grade_id, indicator_id, 1)
                        )

                conn.commit()
                print("✓ База данных инициализирована успешно")

            except Error as e:
                print(f"✗ Ошибка инициализации базы данных: {e}")
                import traceback
                traceback.print_exc()
            finally:
                cursor.close()
        else:
            print("✗ Не удалось подключиться к базе данных")

    def execute_query(self, query, params=()):
        """Выполнение SQL-запроса"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None

    def fetch_all(self, query, params=()):
        """Получение всех результатов запроса"""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchall()
        return []

    def fetch_one(self, query, params=()):
        """Получение одного результата запроса"""
        cursor = self.execute_query(query, params)
        if cursor:
            return cursor.fetchone()
        return None

    def get_competencies_by_subject(self, subject_id):
        """Получение компетенций для предмета"""
        query = """
        SELECT DISTINCT fc.id, fc.code, fc.name, fc.type 
        FROM fgos_competencies fc
        JOIN subjects s ON fc.specialty = s.specialty
        WHERE s.id = ?
        ORDER BY fc.type, fc.code
        """
        return self.fetch_all(query, (subject_id,))

    def get_indicators_by_competency(self, competency_id):
        """Получение индикаторов для компетенции"""
        query = """
        SELECT id, code, description, weight, max_score
        FROM fgos_indicators
        WHERE competency_id = ?
        ORDER BY code
        """
        return self.fetch_all(query, (competency_id,))

    def add_grade_with_indicators(self, grade_data, selected_indicators):
        """Добавление оценки с выбранными индикаторами"""
        try:
            cursor = self.connection.cursor()
            
            # Вставляем оценку
            cursor.execute(
                """INSERT INTO grades 
                (student_id, teacher_id, subject_id, competency_id, grade_value, percentage, comment, date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (grade_data['student_id'], grade_data['teacher_id'], grade_data['subject_id'],
                 grade_data['competency_id'], grade_data['grade_value'], grade_data['percentage'],
                 grade_data['comment'], grade_data['date'])
            )
            
            grade_id = cursor.lastrowid
            
            # Вставляем выбранные индикаторы
            for indicator_id in selected_indicators:
                cursor.execute(
                    "INSERT INTO grade_indicators (grade_id, indicator_id, score) VALUES (?, ?, ?)",
                    (grade_id, indicator_id, 1)
                )
            
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error adding grade with indicators: {e}")
            return False

    def get_student_grades_with_details(self, student_id):
        """Получение оценок студента с деталями по ФГОС"""
        query = """
        SELECT g.id, s.name as subject, fc.code as competency_code, fc.name as competency_name,
               g.grade_value, g.percentage, g.comment, g.date, u.full_name as teacher_name,
               GROUP_CONCAT(fi.description, '; ') as indicators
        FROM grades g
        JOIN subjects s ON g.subject_id = s.id
        JOIN fgos_competencies fc ON g.competency_id = fc.id
        JOIN users u ON g.teacher_id = u.id
        LEFT JOIN grade_indicators gi ON g.id = gi.grade_id
        LEFT JOIN fgos_indicators fi ON gi.indicator_id = fi.id
        WHERE g.student_id = ?
        GROUP BY g.id
        ORDER BY g.date DESC
        """
        return self.fetch_all(query, (student_id,))

    def calculate_grade_from_indicators(self, selected_indicators, competency_id):
        """Расчет оценки на основе выбранных индикаторов"""
        if not selected_indicators:
            return 2, 0  # Если ничего не выбрано - не сформировано
        
        # Получаем все индикаторы для компетенции
        query = "SELECT id FROM fgos_indicators WHERE competency_id = ?"
        all_indicators = self.fetch_all(query, (competency_id,))
        
        if not all_indicators:
            return 2, 0
        
        total_indicators = len(all_indicators)
        selected_count = len(selected_indicators)
        
        # Рассчитываем процент освоения
        percentage = (selected_count / total_indicators) * 100
        
        # Определяем оценку по проценту
        if percentage >= 86:
            return 5, percentage
        elif percentage >= 67:
            return 4, percentage
        elif percentage >= 48:
            return 3, percentage
        else:
            return 2, percentage

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")