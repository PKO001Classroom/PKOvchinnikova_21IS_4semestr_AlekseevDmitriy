from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    ROLE_CHOICES = [
        ('teacher', 'Преподаватель'),
        ('student', 'Студент'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    college_id = models.IntegerField(blank=True, null=True)
    specialty_code = models.CharField(max_length=20, blank=True, null=True)
    group_name = models.CharField(max_length=50, blank=True, null=True)
    
    def is_student(self):
        return self.role == 'student'
    
    def is_teacher(self):
        return self.role == 'teacher'

class Subject(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True, null=True)
    specialty_code = models.CharField(max_length=20)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class FGOSCompetency(models.Model):
    TYPE_CHOICES = [
        ('ПК', 'Профессиональная компетенция'),
        ('ОПК', 'Общепрофессиональная компетенция'),
        ('УК', 'Универсальная компетенция'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=500)
    specialty_code = models.CharField(max_length=20)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
    def __str__(self):
        return self.code

class Grade(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_grades')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teacher_grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    competency_code = models.CharField(max_length=20)
    percentage = models.IntegerField()
    grade_value = models.IntegerField()
    comment = models.TextField()
    
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'subject', 'date'],
                name='one_grade_per_week',
                condition=models.Q(date__week=models.F('date__week'))
            )
        ]
    
    def clean(self):
        # Проверка комментария (минимум 100 символов)
        if len(self.comment) < 100:
            raise ValidationError("Комментарий должен быть не менее 100 символов")
        
        # Проверка процента (0-100)
        if not 0 <= self.percentage <= 100:
            raise ValidationError("Процент должен быть в диапазоне 0-100")
        
        # Проверка оценки (2-5)
        if not 2 <= self.grade_value <= 5:
            raise ValidationError("Оценка должна быть в диапазоне 2-5")
        
        # Проверка одной оценки в неделю
        week_start = self.date - timedelta(days=self.date.weekday())
        week_end = week_start + timedelta(days=6)
        
        existing_grades = Grade.objects.filter(
            student=self.student,
            subject=self.subject,
            date__range=[week_start, week_end]
        )
        
        if self.pk:
            existing_grades = existing_grades.exclude(pk=self.pk)
        
        if existing_grades.exists():
            raise ValidationError("Можно выставлять только одну оценку в неделю по предмету")
    
    def __str__(self):
        return f"{self.student} - {self.subject}: {self.grade_value}"