from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from django.utils import timezone
from datetime import date

def generate_student_report_pdf(student, grades):
    """Генерация PDF отчета для студента"""
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=f"Отчет успеваемости {student.full_name}"
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    story.append(Paragraph(f"Отчет об успеваемости", title_style))
    story.append(Paragraph(f"Студент: {student.full_name}", styles['Heading2']))
    story.append(Paragraph(f"Группа: {student.group_name}", styles['Normal']))
    story.append(Paragraph(f"Специальность: {student.specialty_code}", styles['Normal']))
    story.append(Paragraph(f"Дата отчета: {date.today().strftime('%d.%m.%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Сводная статистика
    if grades:
        avg_grade = sum(g.grade_value for g in grades) / len(grades)
        subjects_count = len(set(g.subject.name for g in grades))
        
        stats_data = [
            ["Показатель", "Значение"],
            ["Средний балл", f"{avg_grade:.2f}"],
            ["Количество предметов", str(subjects_count)],
            ["Всего оценок", str(len(grades))],
        ]
        
        stats_table = Table(stats_data, colWidths=[8*cm, 5*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 30))
    
    # Таблица оценок
    if grades:
        story.append(Paragraph("Детализация оценок:", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        grades_data = [["Предмет", "Дата", "Оценка", "Компетенция", "Комментарий"]]
        
        for grade in grades:
            # Обрезаем комментарий для таблицы
            short_comment = grade.comment[:50] + "..." if len(grade.comment) > 50 else grade.comment
            
            grades_data.append([
                grade.subject.name,
                grade.date.strftime('%d.%m.%Y'),
                str(grade.grade_value),
                grade.competency_code,
                short_comment
            ])
        
        grades_table = Table(grades_data, colWidths=[4*cm, 2.5*cm, 2*cm, 3*cm, 8*cm])
        grades_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(grades_table)
    
    # Подпись
    story.append(Spacer(1, 30))
    story.append(Paragraph("Отчет сгенерирован автоматически", styles['Italic']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer