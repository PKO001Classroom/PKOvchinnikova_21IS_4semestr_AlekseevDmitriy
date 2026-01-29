def validate_comment(comment, min_length=100):
    """Валидация комментария"""
    if len(comment) < min_length:
        return False, f"Комментарий должен быть не менее {min_length} символов"
    
    # Проверяем наличие кода компетенции в комментарии
    if not any(keyword in comment.upper() for keyword in ['ПК', 'ОПК', 'УК']):
        return False, "В комментарии должен быть указан код компетенции (ПК, ОПК или УК)"
    
    return True, "OK"

def validate_indicators(selected_indicators, total_indicators):
    """Валидация выбранных индикаторов"""
    if not selected_indicators:
        return False, "Выберите хотя бы один индикатор освоения"
    
    selected_count = len(selected_indicators)
    percentage = (selected_count / total_indicators) * 100 if total_indicators > 0 else 0
    
    return True, f"Выбрано {selected_count} из {total_indicators} индикаторов ({percentage:.1f}%)"

def calculate_grade_from_percentage(percentage):
    """Расчет оценки из процента освоения"""
    if percentage >= 86:
        return 5, "высокий уровень"
    elif percentage >= 67:
        return 4, "повышенный уровень"
    elif percentage >= 48:
        return 3, "базовый уровень"
    else:
        return 2, "не сформировано"

def get_grade_description(grade_value):
    """Получение описания оценки"""
    descriptions = {
        5: "5 (86-100%): Высокий уровень - полное освоение компетенции, творческое применение",
        4: "4 (67-85%): Повышенный уровень - уверенное применение в типовых ситуациях",
        3: "3 (48-66%): Базовый уровень - освоение основных элементов с поддержкой",
        2: "2 (0-47%): Не сформировано - требуется дополнительное обучение"
    }
    return descriptions.get(grade_value, "Не определена")

def validate_competency_data(competency_code, competency_name):
    """Валидация данных компетенции"""
    if not competency_code:
        return False, "Код компетенции не может быть пустым"
    
    if not competency_name:
        return False, "Название компетенции не может быть пустым"
    
    # Проверяем формат кода компетенции
    if not any(competency_code.upper().startswith(prefix) for prefix in ['ПК', 'ОПК', 'УК']):
        return False, "Код компетенции должен начинаться с ПК, ОПК или УК"
    
    return True, "OK"

def validate_indicator_data(indicator_code, description):
    """Валидация данных индикатора"""
    if not indicator_code:
        return False, "Код индикатора не может быть пустым"
    
    if not description:
        return False, "Описание индикатора не может быть пустым"
    
    if len(description) < 10:
        return False, "Описание индикатора должно содержать не менее 10 символов"
    
    return True, "OK"

def calculate_percentage_from_indicators(selected_count, total_count):
    """Расчет процента освоения из количества индикаторов"""
    if total_count == 0:
        return 0
    return (selected_count / total_count) * 100