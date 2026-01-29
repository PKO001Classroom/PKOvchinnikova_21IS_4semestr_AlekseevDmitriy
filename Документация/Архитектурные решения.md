# Архитектурное решение системы управления учебным процессом (PyQt5 версия)

---

## 1. Введение

**Система:** Desktop-приложение для управления оценками в колледжах с учетом ФГОС СПО  
**Цель:** Автоматизация выставления, хранения и просмотра оценок с ролевым разделением (преподаватель/студент)  
**Подход:** Клиент-серверная архитектура с SQLite базой данных и GUI на PyQt5

---

## 2. Технический стек (упрощенный)

### Бэкенд:
- **Python 3.11+**
- **SQLite3** для локальной базы данных
- **PyQt5** для графического интерфейса

### Архитектура:
- **Модель-Представление-Контроллер (MVC)** упрощенная
- **Локальное хранение данных** без сервера
- **Контейнеризация через Docker** (опционально)

---

## 3. Архитектура системы

```
┌─────────────────────────────────────────────────┐
│                Пользователь                      │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│             PyQt5 GUI Application               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Views   │ │ Controllers││ Models   │       │
│  │ (Windows)│ │ (Logic)   ││ (Classes) │       │
│  └──────────┘ └──────────┘ └──────────┘       │
│  ┌───────────────────────────────────────┐     │
│  │         Бизнес-логика                 │     │
│  │  • Авторизация/роли                   │     │
│  │  • Оценки по ФГОС                     │     │
│  │  • Расчет средних баллов              │     │
│  │  • Проверка комментариев (100+ симв.)│     │
│  └───────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              SQLite Database                    │
│  • Пользователи, оценки, предметы              │
│  • Комментарии                                 │
└─────────────────────────────────────────────────┘
```

---

## 4. Структура проекта

```
edu_journal/
├── main.py                      # Главный файл приложения
├── database.py                  # Работа с базой данных
├── models.py                    # Модели данных (User, Subject, Grade)
├── ui/                          # Пользовательский интерфейс
│   ├── __init__.py
│   ├── login_window.py          # Окно входа
│   ├── student_window.py        # Окно студента
│   └── teacher_window.py        # Окно преподавателя
├── utils/                       # Вспомогательные функции
│   ├── __init__.py
│   └── validators.py           # Валидация данных
├── data/                        # Папка для базы данных
│   └── edu_journal.db          # SQLite база данных
├── requirements.txt             # Зависимости
├── Dockerfile                   # Конфигурация Docker
├── docker-compose.yml          # Docker Compose
├── README.md                   # Документация
└── run_simple.py               # Скрипт для быстрого запуска
```

---

## 5. Основные таблицы базы данных

```sql
-- 1. Пользователи
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('teacher', 'student')),
    full_name TEXT NOT NULL,
    specialty TEXT,
    group_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Предметы
CREATE TABLE subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    code TEXT,
    specialty TEXT
);

-- 3. Оценки
CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    grade_value INTEGER NOT NULL CHECK(grade_value BETWEEN 2 AND 5),
    comment TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (teacher_id) REFERENCES users(id),
    FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- 4. Компетенции ФГОС (упрощенная версия)
CREATE TABLE competencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    specialty TEXT,
    type TEXT CHECK(type IN ('ПК', 'ОПК', 'УК'))
);
```

---

## 6. Ключевые окна приложения

### 6.1. Авторизация:
- **LoginWindow** - Окно входа с полями логин/пароль
- Выбор роли (учитель/студент) для тестирования

### 6.2. Для студентов:
- **StudentWindow** - Главное окно студента
  - Просмотр всех оценок
  - Просмотр комментариев преподавателей
  - Расчет среднего балла
  - Фильтрация по предметам

### 6.3. Для преподавателей:
- **TeacherWindow** - Главное окно преподавателя
  - Просмотр списка студентов
  - Выставление новых оценок
  - Добавление комментариев
  - Просмотр журнала оценок
  - Управление предметами

---

## 7. Бизнес-логика (основные функции)

### 7.1. Расчет оценки по ФГОС:
```python
def calculate_grade(percentage):
    """Преобразует процент в оценку по ФГОС"""
    if 86 <= percentage <= 100:
        return 5, "высокий уровень"
    elif 67 <= percentage <= 85:
        return 4, "повышенный уровень"
    elif 48 <= percentage <= 66:
        return 3, "базовый уровень"
    else:
        return 2, "не сформировано"
```

### 7.2. Проверка комментария:
```python
def validate_comment(comment, min_length=10):
    """Проверяет комментарий на соответствие требованиям"""
    if len(comment) < min_length:
        return False, f"Комментарий должен быть не менее {min_length} символов"
    
    if 'ПК' not in comment and 'ОПК' not in comment:
        return False, "Рекомендуется указать код компетенции (ПК или ОПК)"
    
    return True, "OK"
```

### 7.3. Расчет среднего балла:
```python
def calculate_average(student_id, db_connection):
    """Рассчитывает средний балл для студента"""
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT AVG(grade_value) FROM grades WHERE student_id = ?",
        (student_id,)
    )
    result = cursor.fetchone()
    return result[0] if result and result[0] is not None else 0.0
```

---

## 8. Валидации и ограничения

### Автоматические проверки:
1. **Ролевой доступ** - студенты не могут выставлять оценки
2. **Минимум комментария** - 10 символов обязательно (упрощено для демо)
3. **Валидность оценки** - только 2, 3, 4, 5
4. **Обязательные поля** - все поля формы должны быть заполнены

### Бизнес-правила:
- Преподаватель видит всех студентов
- Студент видит только свои оценки
- Оценки хранятся с указанием даты и времени
- Все изменения логируются

---

## 9. Развертывание и настройка

### Простой вариант (без Docker):
```bash
# 1. Установка зависимостей
pip install PyQt5==5.15.9

# 2. Запуск приложения
python main.py
```

### Вариант с Docker (рекомендуется):
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libxcb-xinerama0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  edu-journal:
    build: .
    container_name: edu_journal_app
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
      - ./data:/app/data
    network_mode: host
```

---

## 10. Этапы разработки

**Неделя 1:** Базовая структура проекта + SQLite база данных  
**Неделя 2:** Система авторизации и роли  
**Неделя 3:** Окно студента (просмотр оценок)  
**Неделя 4:** Окно преподавателя (выставление оценок)  
**Неделя 5:** Валидации по ФГОС + бизнес-логика  
**Неделя 6:** Тестирование и отладка  
**Неделя 7:** Упаковка и документация  
**Неделя 8:** Деплой и финальные правки  

---

## 11. Упрощения для учебного проекта

1. **Нет веб-сервера** - локальное desktop-приложение
2. **Нет API** - прямой доступ к базе данных
3. **Простая аутентификация** - без шифрования паролей (для демо)
4. **SQLite вместо PostgreSQL** - для простоты развертывания
5. **Минимум зависимостей** - только PyQt5
6. **Локальное хранение** - все данные на компьютере пользователя
7. **Упрощенные требования ФГОС** - базовые проверки

---

## 12. Что можно добавить позже

1. **Шифрование паролей** - использование bcrypt или similar
2. **Экспорт в PDF/Excel** - отчеты по успеваемости
3. **Резервное копирование** - автоматический backup базы данных
4. **Сетевой режим** - клиент-серверная архитектура
5. **Уведомления** - системные уведомления о новых оценках
6. **Статистика** - графики и аналитика успеваемости
7. **Мультиязычность** - поддержка нескольких языков

---

## Итог

Такая архитектура:
- ✅ **Простая** для понимания и разработки
- ✅ **Быстрая** в реализации (2-4 недели)
- ✅ **Соответствует основным требованиям** ФГОС СПО
- ✅ **Легкая в развертывании** - один файл .exe или через pip
- ✅ **Идеальна для учебного проекта** - показывает все основные навыки
- ✅ **Кроссплатформенная** - работает на Windows, Linux, Mac

**Основной фокус:** работающая бизнес-логика по ФГОС и удобный интерфейс