class User:
    def __init__(self, user_id, username, password, role, full_name, specialty=None, group_name=None, created_at=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name
        self.specialty = specialty
        self.group_name = group_name
        self.created_at = created_at

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', role='{self.role}', name='{self.full_name}')"

class Subject:
    def __init__(self, subject_id, name, code, specialty, teacher_id=None):
        self.id = subject_id
        self.name = name
        self.code = code
        self.specialty = specialty
        self.teacher_id = teacher_id

    def __repr__(self):
        return f"Subject(id={self.id}, name='{self.name}', code='{self.code}')"

class FgosCompetency:
    """Модель компетенции ФГОС"""
    def __init__(self, competency_id, code, name, description, specialty, type):
        self.id = competency_id
        self.code = code
        self.name = name
        self.description = description
        self.specialty = specialty
        self.type = type  # ПК, ОПК, УК
        self.total_indicators = 0  # Будет установлено позже

    def __repr__(self):
        return f"FgosCompetency(id={self.id}, code='{self.code}', type='{self.type}')"

class FgosIndicator:
    """Модель индикатора освоения ФГОС"""
    def __init__(self, indicator_id, competency_id, code, description, weight=1, max_score=1):
        self.id = indicator_id
        self.competency_id = competency_id
        self.code = code
        self.description = description
        self.weight = weight
        self.max_score = max_score

    def __repr__(self):
        return f"FgosIndicator(id={self.id}, code='{self.code}', weight={self.weight})"

class Grade:
    """Модель оценки с привязкой к ФГОС"""
    def __init__(self, grade_id, student_id, teacher_id, subject_id, competency_id, 
                 grade_value, percentage, comment, date):
        self.id = grade_id
        self.student_id = student_id
        self.teacher_id = teacher_id
        self.subject_id = subject_id
        self.competency_id = competency_id
        self.grade_value = grade_value
        self.percentage = percentage
        self.comment = comment
        self.date = date
        self.selected_indicators = []  # Список выбранных индикаторов

    def add_indicator(self, indicator_id):
        """Добавление индикатора к оценке"""
        self.selected_indicators.append(indicator_id)

    def __repr__(self):
        return f"Grade(id={self.id}, student={self.student_id}, grade={self.grade_value}, date='{self.date}')"

class GradeWithDetails:
    """Модель оценки с деталями для отображения"""
    def __init__(self, grade_id, subject_name, competency_code, competency_name, 
                 competency_type, grade_value, percentage, indicators, comment, 
                 date, teacher_name):
        self.id = grade_id
        self.subject_name = subject_name
        self.competency_code = competency_code
        self.competency_name = competency_name
        self.competency_type = competency_type
        self.grade_value = grade_value
        self.percentage = percentage
        self.indicators = indicators
        self.comment = comment
        self.date = date
        self.teacher_name = teacher_name

    def get_grade_description(self):
        """Получение текстового описания оценки"""
        if self.grade_value == 5:
            return "Высокий уровень (75-100%)"
        elif self.grade_value == 4:
            return "Повышенный уровень (60-74%)"
        elif self.grade_value == 3:
            return "Базовый уровень (50-59%)"
        else:
            return "Не сформировано (0-49%)"

    def __repr__(self):
        return f"GradeWithDetails(id={self.id}, subject='{self.subject_name}', grade={self.grade_value})"

class CompetencyWithIndicators:
    """Модель компетенции с индикаторами"""
    def __init__(self, competency, indicators):
        self.competency = competency
        self.indicators = indicators
        self.total_indicators = len(indicators)
        
    def get_requirements_text(self):
        """Получение текста требований для оценок"""
        if self.total_indicators >= 8:
            return f"Требования: 5 (6-8 из 8), 4 (5 из 8), 3 (4 из 8), 2 (0-3 из 8)"
        elif self.total_indicators >= 6:
            return f"Требования: 5 (5-6 из 6), 4 (4 из 6), 3 (3 из 6), 2 (0-2 из 6)"
        else:
            return f"Требования: 5 (86-100%), 4 (67-85%), 3 (48-66%), 2 (0-47%)"
    
    def __repr__(self):
        return f"CompetencyWithIndicators(competency={self.competency.code}, indicators={len(self.indicators)})"