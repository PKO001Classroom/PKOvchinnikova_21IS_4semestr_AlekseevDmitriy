from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Студент
    path('', views.student_dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/grades/', views.student_grades, name='student_grades'),
    path('student/subjects/', views.student_subjects, name='student_subjects'),
    path('student/report/', views.student_report, name='student_report'),
    
    # Преподаватель
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/groups/', views.teacher_groups, name='teacher_groups'),
    path('teacher/grade/add/', views.add_grade, name='add_grade'),
    path('teacher/reports/', views.teacher_reports, name='teacher_reports'),
]