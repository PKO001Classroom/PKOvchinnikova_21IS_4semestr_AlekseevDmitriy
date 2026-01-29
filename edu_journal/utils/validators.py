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
    
    # Проверка минимального количества для оценки 3
    if total_indicators >= 8 and selected_count < 4:
        return False, f"Для получения оценки 3 необходимо выбрать минимум 4 индикатора из {total_indicators}"
    elif total_indicators >= 6 and selected_count < 3:
        return False, f"Для получения оценки 3 необходимо выбрать минимум 3 индикатора из {total_indicators}"
    
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
        5: "5 (75-100%): Высокий уровень - отличное освоение, творческое применение",
        4: "4 (60-74%): Повышенный уровень - уверенное применение в типовых ситуациях",
        3: "3 (50-59%): Базовый уровень - освоение основных элементов",
        2: "2 (0-49%): Не сформировано - требуется дополнительное обучение"
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

def calculate_grade_by_count(selected_count, total_count):
    """Расчет оценки по количеству выбранных пунктов"""
    if total_count == 0:
        return 2, 0
    
    # Новая логика оценки
    if total_count >= 8:
        if selected_count >= 6:  # 6-8 из 8 (75-100%)
            return 5, (selected_count / total_count) * 100
        elif selected_count >= 5:  # 5 из 8 (62.5%)
            return 4, (selected_count / total_count) * 100
        elif selected_count >= 4:  # 4 из 8 (50%)
            return 3, (selected_count / total_count) * 100
        else:
            return 2, (selected_count / total_count) * 100
    elif total_count >= 6:
        if selected_count >= 5:  # 5-6 из 6 (83-100%)
            return 5, (selected_count / total_count) * 100
        elif selected_count >= 4:  # 4 из 6 (67%)
            return 4, (selected_count / total_count) * 100
        elif selected_count >= 3:  # 3 из 6 (50%)
            return 3, (selected_count / total_count) * 100
        else:
            return 2, (selected_count / total_count) * 100
    else:
        # Для меньшего количества пунктов используем процентную систему
        percentage = (selected_count / total_count) * 100
        if percentage >= 86:
            return 5, percentage
        elif percentage >= 67:
            return 4, percentage
        elif percentage >= 48:
            return 3, percentage
        else:
            return 2, percentage

def get_grade_requirements(total_indicators):
    """Получение требований для получения каждой оценки"""
    if total_indicators >= 8:
        return {
            5: "6-8 индикаторов из 8 (75-100%)",
            4: "5 индикаторов из 8 (62.5%)",
            3: "4 индикатора из 8 (50%)",
            2: "0-3 индикатора из 8 (0-37.5%)"
        }
    elif total_indicators >= 6:
        return {
            5: "5-6 индикаторов из 6 (83-100%)",
            4: "4 индикатора из 6 (67%)",
            3: "3 индикатора из 6 (50%)",
            2: "0-2 индикатора из 6 (0-33%)"
        }
    else:
        return {
            5: "86-100% освоения",
            4: "67-85% освоения",
            3: "48-66% освоения",
            2: "0-47% освоения"
        }