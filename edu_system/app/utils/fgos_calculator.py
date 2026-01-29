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

def calculate_average(student_id, subject_id=None):
    """Рассчитывает средний балл для студента"""
    from ..models import Grade
    
    grades = Grade.objects.filter(student_id=student_id)
    if subject_id:
        grades = grades.filter(subject_id=subject_id)
    
    if not grades.exists():
        return 0
    
    return sum(g.grade_value for g in grades) / len(grades)