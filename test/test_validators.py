"""
Тестирование модуля validators.py
"""
import pytest
from utils.validators import (
    validate_comment,
    validate_grade,
    validate_percentage,
    calculate_grade_from_percentage
)

class TestCommentValidator:
    """Тесты для валидации комментариев"""
    
    def test_validate_comment_success(self):
        """Тест успешной валидации комментария"""
        comment = "Хорошая работа по теме ПК 1.1. Студент продемонстрировал понимание основных концепций."
        result, message = validate_comment(comment, min_length=10)
        
        assert result is True
        assert message == "OK"
    
    def test_validate_comment_too_short(self):
        """Тест слишком короткого комментария"""
        comment = "ок"
        result, message = validate_comment(comment, min_length=10)
        
        assert result is False
        assert "не менее 10 символов" in message
    
    def test_validate_comment_empty(self):
        """Тест пустого комментария"""
        comment = ""
        result, message = validate_comment(comment, min_length=5)
        
        assert result is False
        assert "не менее 5 символов" in message
    
    def test_validate_comment_with_default_min_length(self):
        """Тест с минимальной длиной по умолчанию"""
        # Должно быть минимум 100 символов по умолчанию
        short_comment = "Короткий комментарий"
        result, message = validate_comment(short_comment)
        
        assert result is False
        assert "не менее 100 символов" in message
    
    def test_validate_comment_with_competency_recommendation(self):
        """Тест рекомендации по указанию компетенции"""
        comment_without_competency = "Хорошая работа, но можно лучше."
        comment_with_competency = "Хорошая работа по ПК 2.3. ОПК 1.1 освоен."
        
        # Тест без компетенции - должно быть предупреждение
        # (в текущей реализации нет такого предупреждения)
        # Этот тест можно использовать если добавим такую проверку
        
        result1, _ = validate_comment(comment_without_competency, min_length=10)
        result2, _ = validate_comment(comment_with_competency, min_length=10)
        
        # Оба комментария должны быть валидны по длине
        assert result1 is True
        assert result2 is True

class TestGradeValidator:
    """Тесты для валидации оценок"""
    
    @pytest.mark.parametrize("grade", [2, 3, 4, 5])
    def test_validate_grade_valid_values(self, grade):
        """Тест валидных значений оценок"""
        result, message = validate_grade(grade)
        assert result is True
        assert message == "OK"
    
    @pytest.mark.parametrize("grade", [0, 1, 6, 10, -1])
    def test_validate_grade_invalid_values(self, grade):
        """Тест невалидных значений оценок"""
        result, message = validate_grade(grade)
        assert result is False
        assert "диапазоне от 2 до 5" in message
    
    @pytest.mark.parametrize("grade", ["5", 4.5, None, [], {}])
    def test_validate_grade_not_integer(self, grade):
        """Тест нецелочисленных значений"""
        result, message = validate_grade(grade)
        assert result is False
        assert "целым числом" in message
    
    def test_validate_grade_boundary_values(self):
        """Тест граничных значений"""
        # Граничные валидные значения
        assert validate_grade(2)[0] is True  # Минимальная валидная
        assert validate_grade(5)[0] is True  # Максимальная валидная
        
        # Граничные невалидные значения
        assert validate_grade(1)[0] is False  # Ниже минимума
        assert validate_grade(6)[0] is False  # Выше максимума

class TestPercentageValidator:
    """Тесты для валидации процентов"""
    
    @pytest.mark.parametrize("percentage", [0, 50, 100])
    def test_validate_percentage_valid_values(self, percentage):
        """Тест валидных значений процентов"""
        result, message = validate_percentage(percentage)
        assert result is True
        assert message == "OK"
    
    @pytest.mark.parametrize("percentage", [-1, 101, 150, -10])
    def test_validate_percentage_invalid_values(self, percentage):
        """Тест невалидных значений процентов"""
        result, message = validate_percentage(percentage)
        assert result is False
        assert "диапазоне от 0 до 100" in message
    
    @pytest.mark.parametrize("percentage", ["50", 75.5, None])
    def test_validate_percentage_not_integer(self, percentage):
        """Тест нецелочисленных процентов"""
        result, message = validate_percentage(percentage)
        assert result is False
        assert "целым числом" in message
    
    def test_validate_percentage_boundary_values(self):
        """Тест граничных значений процентов"""
        assert validate_percentage(0)[0] is True   # Минимальный валидный
        assert validate_percentage(100)[0] is True # Максимальный валидный
        assert validate_percentage(-1)[0] is False # Ниже минимума
        assert validate_percentage(101)[0] is False # Выше максимума

class TestGradeCalculator:
    """Тесты для расчета оценки из процента"""
    
    @pytest.mark.parametrize("percentage,expected_grade", [
        (100, 5), (95, 5), (90, 5), (86, 5),  # 86-100% -> 5
        (85, 4), (80, 4), (75, 4), (67, 4),   # 67-85% -> 4
        (66, 3), (60, 3), (55, 3), (48, 3),   # 48-66% -> 3
        (47, 2), (30, 2), (10, 2), (0, 2)     # 0-47% -> 2
    ])
    def test_calculate_grade_from_percentage(self, percentage, expected_grade):
        """Тест расчета оценки из процента"""
        grade = calculate_grade_from_percentage(percentage)
        assert grade == expected_grade
    
    def test_calculate_grade_edge_cases(self):
        """Тест граничных случаев расчета"""
        # Точные границы
        assert calculate_grade_from_percentage(86) == 5
        assert calculate_grade_from_percentage(85) == 4
        assert calculate_grade_from_percentage(67) == 4
        assert calculate_grade_from_percentage(66) == 3
        assert calculate_grade_from_percentage(48) == 3
        assert calculate_grade_from_percentage(47) == 2
    
    @pytest.mark.parametrize("percentage", [-10, 150, 1000])
    def test_calculate_grade_out_of_range(self, percentage):
        """Тест расчета с процентами вне диапазона"""
        # В текущей реализации нет проверки диапазона
        # Этот тест можно добавить если реализуем проверку
        grade = calculate_grade_from_percentage(percentage)
        # Пока просто проверяем что функция не падает
        assert grade in [2, 3, 4, 5]