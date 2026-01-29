def validate_comment(comment, min_length=100):
    """Валидация комментария"""
    if len(comment) < min_length:
        return False, f"Комментарий должен быть не менее {min_length} символов"
    return True, "OK"


def validate_grade(grade_value):
    """Валидация оценки"""
    if not isinstance(grade_value, int):
        return False, "Оценка должна быть целым числом"
    
    if grade_value < 2 or grade_value > 5:
        return False, "Оценка должна быть в диапазоне от 2 до 5"
    
    return True, "OK"


def validate_percentage(percentage):
    """Валидация процента освоения"""
    if not isinstance(percentage, int):
        return False, "Процент должен быть целым числом"
    
    if percentage < 0 or percentage > 100:
        return False, "Процент должен быть в диапазоне от 0 до 100"
    
    return True, "OK"


def calculate_grade_from_percentage(percentage):
    """Расчет оценки по проценту освоения (ФГОС)"""
    if percentage >= 86:
        return 5
    elif percentage >= 67:
        return 4
    elif percentage >= 48:
        return 3
    else:
        return 2