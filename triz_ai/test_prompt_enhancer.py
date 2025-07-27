from prompt_enhancer import enhance_formula


def test_enhance_formula_basic():
    formula = "Устройство, включающее насос, отличающийся тем, что дополнительно содержит датчик температуры."
    result = enhance_formula(formula, openai_api_key=None)
    assert "title" in result
    assert "non_obvious_suggestions" in result
    assert "justification" in result
    assert result["title"] != ""
    assert result["non_obvious_suggestions"] != ""
    assert result["justification"] != ""


def test_enhance_formula_no_distinctive():
    formula = "Способ обработки данных, включающий известные действия и больше ничего."
    result = enhance_formula(formula, openai_api_key=None)
    # Should still produce title and fallback suggestions
    assert result["title"] != ""
    assert "затруднительна" in result["non_obvious_suggestions"] or result["non_obvious_suggestions"] != ""