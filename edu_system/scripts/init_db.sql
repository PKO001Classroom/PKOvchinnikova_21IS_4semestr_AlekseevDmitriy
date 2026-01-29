-- Инициализация базы данных системы управления учебным процессом

-- Создание пользователей с хешированными паролями (пароль для всех: password123)
INSERT INTO auth_user (username, password, email, first_name, last_name, is_staff, is_active, is_superuser, date_joined) VALUES
('teacher1', 'pbkdf2_sha256$600000$abc123$teacher1hash', 'teacher1@college.ru', 'Иван', 'Иванов', true, true, false, NOW()),
('student1', 'pbkdf2_sha256$600000$def456$student1hash', 'student1@college.ru', 'Петр', 'Петров', false, true, false, NOW()),
('student2', 'pbkdf2_sha256$600000$ghi789$student2hash', 'student2@college.ru', 'Анна', 'Сидорова', false, true, false, NOW());

-- Обновление профилей пользователей
INSERT INTO app_user (user_ptr_id, role, college_id, specialty_code, group_name) 
SELECT id, 'teacher', 1, '15.02.01', 'ТМ-101' FROM auth_user WHERE username = 'teacher1'
ON CONFLICT DO NOTHING;

INSERT INTO app_user (user_ptr_id, role, college_id, specialty_code, group_name) 
SELECT id, 'student', 1, '15.02.01', 'ТМ-101' FROM auth_user WHERE username = 'student1'
ON CONFLICT DO NOTHING;

INSERT INTO app_user (user_ptr_id, role, college_id, specialty_code, group_name) 
SELECT id, 'student', 1, '15.02.01', 'ТМ-101' FROM auth_user WHERE username = 'student2'
ON CONFLICT DO NOTHING;

-- Добавление предметов
INSERT INTO app_subject (name, code, specialty_code, teacher_id) VALUES
('Основы программирования', 'ОП.01', '15.02.01', 
    (SELECT id FROM auth_user WHERE username = 'teacher1')),
('Технология сварки', 'ПМ.02', '15.02.01', 
    (SELECT id FROM auth_user WHERE username = 'teacher1')),
('Электротехника', 'ОП.03', '15.02.01', 
    (SELECT id FROM auth_user WHERE username = 'teacher1'));

-- Компетенции ФГОС для специальности 15.02.01
INSERT INTO app_fgoscompetency (code, name, specialty_code, type) VALUES
('ПК 1.1', 'Выполнять слесарные работы', '15.02.01', 'ПК'),
('ПК 1.2', 'Выполнять токарные работы', '15.02.01', 'ПК'),
('ПК 1.3', 'Выполнять фрезерные работы', '15.02.01', 'ПК'),
('ПК 2.1', 'Читать технические чертежи', '15.02.01', 'ПК'),
('ПК 2.2', 'Разрабатывать технологическую документацию', '15.02.01', 'ПК'),
('ОПК 1.1', 'Работать в команде', '15.02.01', 'ОПК'),
('ОПК 1.2', 'Организовывать рабочее место', '15.02.01', 'ОПК'),
('ОПК 2.1', 'Применять нормативную документацию', '15.02.01', 'ОПК'),
('УК 1.1', 'Самостоятельно учиться', '15.02.01', 'УК'),
('УК 2.1', 'Работать с информацией', '15.02.01', 'УК');

-- Тестовые оценки
INSERT INTO app_grade (student_id, teacher_id, subject_id, competency_code, percentage, grade_value, comment, date, created_at) VALUES
(
    (SELECT id FROM auth_user WHERE username = 'student1'),
    (SELECT id FROM auth_user WHERE username = 'teacher1'),
    (SELECT id FROM app_subject WHERE name = 'Основы программирования'),
    'ПК 2.1',
    88,
    5,
    'Студент Петров П.П. продемонстрировал ПК 2.1 в ходе выполнения лабораторной работы по чтению чертежей программного кода. Правильно определил все основные конструкции языка Python, грамотно прочитал UML-диаграммы. Показал отличное понимание принципов объектно-ориентированного программирования. Рекомендуется участие в олимпиаде по программированию.',
    '2024-01-15',
    NOW()
),
(
    (SELECT id FROM auth_user WHERE username = 'student1'),
    (SELECT id FROM auth_user WHERE username = 'teacher1'),
    (SELECT id FROM app_subject WHERE name = 'Технология сварки'),
    'ПК 1.1',
    72,
    4,
    'Студент Петров П.П. освоил ПК 1.1 по выполнению слесарных работ на 72%. Выполнил сборку металлоконструкции согласно техническому заданию, правильно подобрал инструменты. Допустил незначительные ошибки при измерении зазоров. Рекомендуется дополнительная практика по работе со штангенциркулем и микрометром для повышения точности измерений.',
    '2024-01-20',
    NOW()
),
(
    (SELECT id FROM auth_user WHERE username = 'student2'),
    (SELECT id FROM auth_user WHERE username = 'teacher1'),
    (SELECT id FROM app_subject WHERE name = 'Основы программирования'),
    'ПК 2.1',
    65,
    3,
    'Студент Сидорова А.С. продемонстрировала базовый уровень освоения ПК 2.1. Справилась с чтением простых блок-схем, но испытывала затруднения при анализе сложных алгоритмов. Требуется дополнительная работа над пониманием рекурсивных функций и структур данных. Рекомендуется выполнить дополнительные упражнения из учебного пособия.',
    '2024-01-16',
    NOW()
),
(
    (SELECT id FROM auth_user WHERE username = 'student2'),
    (SELECT id FROM auth_user WHERE username = 'teacher1'),
    (SELECT id FROM app_subject WHERE name = 'Электротехника'),
    'ОПК 2.1',
    92,
    5,
    'Студент Сидорова А.С. показала отличное знание ОПК 2.1 по применению нормативной документации. Грамотно использовала ГОСТы при расчете электрических цепей, правильно определила номиналы компонентов по справочникам. Проявила инициативу в поиске актуальных стандартов. Рекомендуется для участия в научно-практической конференции.',
    '2024-01-18',
    NOW()
);

-- Сообщение об успешном завершении
DO $$
BEGIN
    RAISE NOTICE 'База данных успешно инициализирована';
    RAISE NOTICE 'Тестовые пользователи созданы:';
    RAISE NOTICE 'Преподаватель: teacher1 / password123';
    RAISE NOTICE 'Студент 1: student1 / password123';
    RAISE NOTICE 'Студент 2: student2 / password123';
END $$;