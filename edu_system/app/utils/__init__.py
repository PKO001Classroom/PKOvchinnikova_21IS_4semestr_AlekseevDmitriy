# Утилиты для системы управления учебным процессом

from .fgos_calculator import calculate_grade, calculate_average
from .validators import validate_comment
from .reports import generate_student_report_pdf

__all__ = [
    'calculate_grade',
    'calculate_average',
    'validate_comment',
    'generate_student_report_pdf',
]

# Дополнительные функции-помощники для шаблонов
def filter_grade(queryset, grade_value):
    """Фильтр для отображения оценок по значению"""
    return [g for g in queryset if g.grade_value == grade_value]

def avg_grade(queryset):
    """Среднее значение оценок"""
    if not queryset:
        return 0
    return sum(g.grade_value for g in queryset) / len(queryset)

def get_subject_by_name(subjects, name):
    """Получить предмет по имени"""
    for subject in subjects:
        if subject.name == name:
            return subject
    return None

def best_student(queryset):
    """Лучший студент по оценкам"""
    if not queryset:
        return None
    
    # Группируем по студенту и считаем средний балл
    students = {}
    for grade in queryset:
        if grade.student not in students:
            students[grade.student] = []
        students[grade.student].append(grade.grade_value)
    
    # Находим лучшего
    best = None
    best_avg = 0
    
    for student, grades in students.items():
        avg = sum(grades) / len(grades)
        if avg > best_avg:
            best_avg = avg
            best = {
                'student': student,
                'avg_grade': avg,
                'grade_value': max(grades)
            }
    
    return best

# Регистрируем функции для использования в шаблонах
from django.template import Library
register = Library()

register.filter('filter_grade', filter_grade)
register.filter('avg_grade', avg_grade)
register.filter('get_subject_by_name', get_subject_by_name)
register.filter('best_student', best_student)
register.filter('percentage', lambda part, whole: (part / whole * 100) if whole else 0)