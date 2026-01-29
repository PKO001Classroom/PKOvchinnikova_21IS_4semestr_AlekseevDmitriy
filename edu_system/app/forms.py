from django import forms
from .models import Grade, User, Subject, FGOSCompetency
from django.utils import timezone

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'competency_code', 'percentage', 'comment', 'date']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Минимум 100 символов...'}),
            'date': forms.DateInput(attrs={'type': 'date', 'value': timezone.now().date()}),
        }
    
    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        
        if self.teacher:
            # Ограничиваем выбор студентов теми, кого преподает учитель
            self.fields['student'].queryset = User.objects.filter(
                role='student',
                grade__teacher=self.teacher
            ).distinct()
            
            # Ограничиваем выбор предметов теми, что ведет учитель
            self.fields['subject'].queryset = Subject.objects.filter(teacher=self.teacher)
            
            # Добавляем выбор компетенций
            specialty_codes = self.teacher.subject_set.values_list('specialty_code', flat=True).distinct()
            competencies = FGOSCompetency.objects.filter(specialty_code__in=specialty_codes)
            self.fields['competency_code'] = forms.ModelChoiceField(
                queryset=competencies,
                label='Компетенция ФГОС'
            )