import sqlite3
import os
from sqlite3 import Error

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
        """Инициализация базы данных с тестовыми данными"""
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
                    group_name TEXT
                )
                ''')

                # Создание таблицы предметов
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT,
                    specialty TEXT
                )
                ''')

                # Создание таблицы оценок
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    grade_value INTEGER NOT NULL CHECK(grade_value BETWEEN 2 AND 5),
                    comment TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (student_id) REFERENCES users (id),
                    FOREIGN KEY (teacher_id) REFERENCES users (id),
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
                ''')

                # Добавление тестовых пользователей
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    print("Добавление тестовых пользователей...")
                    test_users = [
                        ('teacher1', '123456', 'teacher', 'Иванов Иван Иванович', '15.02.01', 'Группа 101'),
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
                        ('Математика', 'МАТ-101', '15.02.01'),
                        ('Программирование', 'ПРОГ-102', '15.02.01'),
                        ('Базы данных', 'БД-103', '15.02.01'),
                    ]
                    cursor.executemany(
                        "INSERT INTO subjects (name, code, specialty) VALUES (?, ?, ?)",
                        test_subjects
                    )

                # Добавление тестовых оценок
                cursor.execute("SELECT COUNT(*) FROM grades")
                if cursor.fetchone()[0] == 0:
                    print("Добавление тестовых оценок...")
                    test_grades = [
                        (2, 1, 1, 5, 'Отличное понимание темы. ПК 1.1 освоен на высоком уровне.', '2024-01-15'),
                        (2, 1, 2, 4, 'Хорошие результаты. ПК 2.1 освоен уверенно.', '2024-01-16'),
                        (3, 1, 1, 3, 'Требуется дополнительная практика. ПК 1.2 требует доработки.', '2024-01-15'),
                    ]
                    cursor.executemany(
                        "INSERT INTO grades (student_id, teacher_id, subject_id, grade_value, comment, date) VALUES (?, ?, ?, ?, ?, ?)",
                        test_grades
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

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")