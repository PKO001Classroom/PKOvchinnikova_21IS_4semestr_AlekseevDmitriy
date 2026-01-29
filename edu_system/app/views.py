from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg
from .models import User, Subject, Grade, FGOSCompetency
from .forms import GradeForm
from .utils.fgos_calculator import calculate_grade
from .utils.validators import validate_comment
from django.http import HttpResponse
import json
from .utils.reports import generate_student_report_pdf
from django.utils import timezone



def student_check(user):
    return user.is_authenticated and user.is_student()

def teacher_check(user):
    return user.is_authenticated and user.is_teacher()

@login_required
def index(request):
    if request.user.is_student():
        return redirect('student_dashboard')
    elif request.user.is_teacher():
        return redirect('teacher_dashboard')
    return redirect('login')

@login_required
@user_passes_test(student_check)
def student_dashboard(request):
    context = {
        'user': request.user,
        'recent_grades': Grade.objects.filter(student=request.user).order_by('-date')[:5],
    }
    return render(request, 'student/dashboard.html', context)

@login_required
@user_passes_test(student_check)
def student_grades(request):
    grades = Grade.objects.filter(student=request.user).order_by('-date')
    context = {
        'grades': grades,
    }
    return render(request, 'student/grades.html', context)

@login_required
@user_passes_test(student_check)
def student_subjects(request):
    # Получаем предметы студента через оценки
    subjects = Subject.objects.filter(
        grade__student=request.user
    ).distinct()
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'student/subjects.html', context)

@login_required
@user_passes_test(student_check)
def student_report(request):
    grades = Grade.objects.filter(student=request.user)
    
    # Рассчитываем средний балл
    avg_grade = grades.aggregate(Avg('grade_value'))['grade_value__avg'] or 0
    
    context = {
        'grades': grades,
        'avg_grade': round(avg_grade, 2),
    }
    return render(request, 'student/report.html', context)

@login_required
@user_passes_test(teacher_check)
def teacher_dashboard(request):
    context = {
        'user': request.user,
        'subjects_count': Subject.objects.filter(teacher=request.user).count(),
        'grades_count': Grade.objects.filter(teacher=request.user).count(),
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
@user_passes_test(teacher_check)
def teacher_groups(request):
    # Получаем уникальные группы студентов, которых обучает преподаватель
    groups = User.objects.filter(
        role='student',
        grade__teacher=request.user
    ).values('group_name').distinct()
    
    context = {
        'groups': groups,
    }
    return render(request, 'teacher/groups.html', context)

@login_required
@user_passes_test(teacher_check)
def add_grade(request):
    if request.method == 'POST':
        form = GradeForm(request.POST, teacher=request.user)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.teacher = request.user
            
            # Автоматический расчет оценки по проценту
            grade_value, level = calculate_grade(grade.percentage)
            grade.grade_value = grade_value
            
            # Валидация комментария
            is_valid, error_msg = validate_comment(grade.comment, grade.competency_code)
            if not is_valid:
                messages.error(request, error_msg)
                return render(request, 'teacher/grade_add.html', {'form': form})
            
            try:
                grade.full_clean()
                grade.save()
                messages.success(request, 'Оценка успешно добавлена')
                return redirect('teacher_dashboard')
            except Exception as e:
                messages.error(request, f'Ошибка: {e}')
    else:
        form = GradeForm(teacher=request.user)
    
    return render(request, 'teacher/grade_add.html', {'form': form})

@login_required
@user_passes_test(teacher_check)
def teacher_reports(request):
    grades = Grade.objects.filter(teacher=request.user)
    
    # Статистика
    avg_by_subject = {}
    subjects = Subject.objects.filter(teacher=request.user)
    
    for subject in subjects:
        subject_grades = grades.filter(subject=subject)
        avg = subject_grades.aggregate(Avg('grade_value'))['grade_value__avg']
        if avg:
            avg_by_subject[subject.name] = round(avg, 2)
    
    context = {
        'grades': grades,
        'avg_by_subject': avg_by_subject,
    }
    return render(request, 'teacher/reports.html', context)
    @login_required
@user_passes_test(student_check)
def download_report(request):
    """Скачивание PDF отчета"""
    grades = Grade.objects.filter(student=request.user)
    pdf_buffer = generate_student_report_pdf(request.user, grades)
    
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{request.user.username}_{timezone.now().date()}.pdf"'
    return response

@login_required
@user_passes_test(teacher_check)
def api_student_grades(request, student_id):
    """API для получения оценок студента"""
    try:
        student = User.objects.get(id=student_id, role='student')
        grades = Grade.objects.filter(student=student, teacher=request.user)
        
        data = {
            'student': student.get_full_name(),
            'grades': [
                {
                    'subject': grade.subject.name,
                    'date': grade.date.strftime('%d.%m.%Y'),
                    'grade_value': grade.grade_value,
                    'comment': grade.comment,
                    'competency_code': grade.competency_code
                }
                for grade in grades
            ]
        }
        
        return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='application/json')
    except User.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'Student not found'}), status=404)

# Обновите функцию student_report для поддержки PDF
@login_required
@user_passes_test(student_check)
def student_report(request):
    grades = Grade.objects.filter(student=request.user)
    
    # Рассчитываем средний балл
    avg_grade = grades.aggregate(Avg('grade_value'))['grade_value__avg'] or 0
    
    # Генерация PDF при запросе
    if request.method == 'POST' and 'generate_pdf' in request.POST:
        return download_report(request)
    
    context = {
        'grades': grades,
        'avg_grade': round(avg_grade, 2),
        'pdf_generated': False
    }
    return render(request, 'student/report.html', context)