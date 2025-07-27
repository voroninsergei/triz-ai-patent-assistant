import re

from generate_formula import generate_formula


def test_generate_formula_short():
    idea = "Устройство для подачи топлива с насосом"
    formula = generate_formula(idea)
    # Should produce non‑empty formula containing name
    assert formula.startswith("Устройство для")
    # Should mention насос
    assert "насос" in formula.lower()


def test_generate_formula_long():
    idea = (
        "Название: Система охлаждения двигателя.\n"
        "Известные признаки: содержит насос, радиатор и вентилятор.\n"
        "Отличительные признаки: имеет датчик температуры, управляющий скоростью вентилятора.\n"
        "Эффект: обеспечивает стабильную температуру без перегрева."
    )
    formula = generate_formula(idea)
    # Should contain 'отличающийся тем'
    assert "отличающийся тем" in formula
    # Should include датчик температуры
    assert "датчик" in formula.lower()
    # Should end with a period
    assert formula.strip().endswith(".")


def test_generate_formula_medium_no_effect():
    idea = (
        "Название: Приспособление для очистки воды.\n"
        "Известные признаки: фильтр, корпус.\n"
        "Отличительные признаки: использование наноматериала в фильтре."
    )
    formula = generate_formula(idea)
    # Should include наноматериал
    assert "наноматери" in formula.lower()
    # Without effect, formula ends with period
    assert formula.strip().endswith(".")