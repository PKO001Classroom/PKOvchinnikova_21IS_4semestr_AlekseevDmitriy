def validate_comment(comment, competency_code):
    """Проверяет комментарий на соответствие требованиям"""
    if len(comment) < 100:
        return False, "Комментарий должен быть не менее 100 символов"
    
    if competency_code not in comment:
        return False, f"Укажите код компетенции ({competency_code})"
    
    return True, "OK"