"""
Module providing a high‑level assessment of an invention's patentability.

The function ``assess_patentability`` orchestrates extraction of patent
features, analysis of novelty, evaluation of non‑obviousness and a final
decision about patentability.  It leverages existing utilities:

* ``generate_formula`` / ``extract_features`` from ``generate_formula.py`` to
  build a first claim and isolate distinctive features.
* ``check_novelty`` from ``check_novelty.py`` to determine whether each
  feature is new relative to known prototypes.
* ``assess_non_obviousness`` (defined in this module) to provide a rough
  estimate of inventive step based on heuristic rules.  In a production
  setting, this function should be replaced with a robust analysis or
  integrated into the LLM evaluation pipeline described in earlier
  instructions.

The final output aggregates these results and makes a simple decision:

* If no features are new → not patentable.
* If features are new but all are obvious → not patentable.
* If there are new and non‑obvious features and an effect is claimed → patentable.

Example::

    from assess_patentability import assess_patentability

    idea = (
        'Название: Интеллектуальная система управления освещением\n'
        'Известные признаки: содержит датчики освещённости и контроллер\n'
        'Отличительные признаки: снабжён беспроводным модулем связи, с возможностью автоматической адаптации яркости\n'
        'Эффект: обеспечивает энергосбережение'
    )
    prototypes = [
        {'id': 'RU123456A', 'text': 'Система освещения, содержащая датчики освещённости и контроллер.'},
        {'id': 'RU789012B', 'text': 'Устройство с беспроводным модулем связи для управления бытовыми приборами.'},
    ]
    report = assess_patentability(idea, prototypes)
    print(report)
"""

from typing import List, Dict, Any, Optional, Union, Callable

from generate_formula import generate_formula, extract_features
from check_novelty import check_novelty


def assess_non_obviousness(
    distinctive_features: List[str],
    novelty_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Provide a heuristic assessment of non‑obviousness for distinctive features.

    For each feature, assign a rating from 1 to 5 (5 means highly non‑obvious)
    and a status "obvious" or "non‑obvious".  The current implementation
    relies on simple heuristics: new features that are lengthy or contain
    compound phrases like "комбинация", "автомат", "интеллект" or
    "снабжён" are considered more inventive.  Features marked as known in
    ``novelty_data`` are assumed obvious and receive a low rating.  The
    function also produces an overall conclusion.

    Parameters
    ----------
    distinctive_features:
        List of extracted distinctive features.

    novelty_data:
        Output from ``check_novelty()['features']``.  It must include the
        status "известный"/"новый" for each feature.

    Returns
    -------
    dict
        ``features``: list of per‑feature assessments with keys
        ``feature``, ``rating``, ``status`` ("non‑obvious"/"obvious") and
        ``reasoning``; ``conclusion``: overall boolean and textual
        summary.
    """
    assessments = []
    any_non_obvious = False

    # Map feature text to novelty status for convenience
    novelty_map = {item["feature"]: item.get("status") for item in novelty_data}

    for feature in distinctive_features:
        novelty_status = novelty_map.get(feature, "известный")
        # Default rating and reasoning
        rating = 1
        status = "obvious"
        reasoning_parts = []

        if novelty_status == "известный":
            rating = 1
            status = "obvious"
            reasoning_parts.append("Признак соответствует известному уровню техники.")
        else:
            # feature is new; evaluate complexity
            length_score = len(feature)
            keywords = ["комбинация", "автомат", "интеллект", "снабж" ]
            keyword_hits = sum(1 for kw in keywords if kw in feature.lower())
            # heuristic: base score on length and keyword presence
            base_score = min(5, 2 + keyword_hits + (1 if length_score > 40 else 0))
            rating = base_score
            status = "non‑obvious" if rating >= 4 else "obvious"
            if keyword_hits:
                reasoning_parts.append("Содержит сложные или комбинированные элементы.")
            if length_score > 40:
                reasoning_parts.append("Длинная формулировка указывает на комплексный характер признака.")
            if status == "non‑obvious":
                reasoning_parts.append("Признак может требовать изобретательского уровня.")
            else:
                reasoning_parts.append("Несмотря на новизну, улучшения кажутся предсказуемыми.")
            if status == "non‑obvious":
                any_non_obvious = True

        assessments.append({
            "feature": feature,
            "rating": rating,
            "status": status,
            "reasoning": ' '.join(reasoning_parts)
        })

    conclusion = {
        "has_non_obvious": any_non_obvious,
        "summary": (
            "Обнаружены неочевидные признаки." if any_non_obvious else
            "Все признаки очевидны."
        )
    }
    return {"features": assessments, "conclusion": conclusion}


def assess_patentability(
    idea: str,
    prototypes: Optional[List[Union[str, Dict[str, Any]]]] = None,
    *,
    similarity_threshold: float = 0.6,
    top_n_matches: Optional[int] = 1,
    search_fn: Optional[
        Callable[[str, List[Union[str, Dict[str, Any]]], float], List[Dict[str, Any]]]
    ] = None,
) -> Dict[str, Any]:
    """Evaluate the overall patentability of an invention.

    This function combines feature extraction, novelty assessment and
    non‑obviousness analysis into a single report.  It uses
    ``generate_formula`` to produce the first claim and extracts
    distinctive features via ``extract_features``.  Novelty is assessed
    through ``check_novelty``.  Non‑obviousness is estimated using
    ``assess_non_obviousness``, which currently implements simple
    heuristics but can be replaced with an AI‑driven evaluator.

    Parameters
    ----------
    idea:
        The description of the invention.

    prototypes:
        A list of known patent descriptions (strings or dicts) used by
        ``check_novelty``.

    similarity_threshold:
        Threshold for fuzzy matching in novelty analysis.

    top_n_matches:
        Number of matches per feature to return from novelty analysis.

    search_fn:
        Optional custom search function for novelty analysis; see
        ``check_novelty``.

    Returns
    -------
    dict
        Aggregated report with keys ``formula``, ``novelty``,
        ``non_obviousness`` and ``patentability_summary``.
    """
    # Generate claim and extract features
    formula = generate_formula(idea)
    features = extract_features(idea)
    distinctive_raw = features.get("distinctive", "")
    # Split raw distinctive features into list
    from check_novelty import _split_features  # reuse splitting logic
    distinctive_features = _split_features(distinctive_raw) if distinctive_raw else []

    # Assess novelty
    novelty_report = check_novelty(
        idea,
        prototypes or [],
        similarity_threshold=similarity_threshold,
        top_n_matches=top_n_matches,
        search_fn=search_fn,
    )
    novelty_features = novelty_report.get("features", [])

    # Assess non‑obviousness
    non_obviousness_report = assess_non_obviousness(distinctive_features, novelty_features)

    # Determine final patentability
    is_new = any(item.get("status") == "новый" for item in novelty_features)
    has_non_obvious = non_obviousness_report["conclusion"]["has_non_obvious"]
    has_effect = bool(features.get("effect"))
    is_patentable = bool(is_new and has_non_obvious and has_effect)
    if not is_new:
        reason = "Отсутствуют новые признаки."
    elif not has_non_obvious:
        reason = "Все новые признаки очевидны."
    elif not has_effect:
        reason = "Не описан технический эффект."
    else:
        reason = "Есть новые и неочевидные признаки и заявленный эффект."

    summary = {
        "is_patentable": is_patentable,
        "reason": reason
    }

    return {
        "formula": formula,
        "novelty": novelty_report,
        "non_obviousness": non_obviousness_report,
        "patentability_summary": summary
    }


__all__ = ["assess_patentability", "assess_non_obviousness"]