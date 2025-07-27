"""
Utility for assessing the novelty of distinctive features extracted from an
invention description.

The function defined in this module, ``check_novelty``, uses the
``extract_features`` helper from ``generate_formula`` to obtain the
distinctive features of an idea.  It then compares each feature against a
database of known patent descriptions (supplied by the caller) or an
external search API (e.g., Espacenet or Google Patents).  If a feature
appears verbatim or with a close synonym in the prior art, it is marked
as "известный" (known); otherwise it is marked as "новый" (novel).

Because this environment does not have access to real patent databases,
``check_novelty`` includes a basic substring and similarity search over
a user‑provided list of prototype descriptions.  Integration with real
patent APIs can be implemented by replacing the ``_search_in_prototypes``
function.

Returns a structured result containing the status of each feature and
a high‑level conclusion about whether the invention as a whole appears
novel.

    Example::

        from check_novelty import check_novelty

        # Idea description with labels; note the use of single quotes to avoid
        # terminating the docstring prematurely.
        idea_desc = (
            'Название: Устройство для очистки воды\n'
            'Известные признаки: содержит корпус и фильтрующий элемент\n'
            'Отличительные признаки: снабжён встроенным ультрафиолетовым излучателем\n'
            'Эффект: обеспечивает обеззараживание воды'
        )

        prototypes = ['Фильтр для воды, содержащий корпус и фильтрующий элемент со сменным картриджем']
        result = check_novelty(idea_desc, prototypes)
        print(result)
"""

from typing import List, Dict, Any, Optional, Union, Callable
import difflib
from generate_formula import extract_features


def _similar(a: str, b: str, threshold: float = 0.7) -> bool:
    """Return True if two strings are semantically similar.

    The default implementation relies on SequenceMatcher to compute a
    similarity ratio between lower‑cased strings.  For better semantic
    normalization, both strings are preprocessed by removing punctuation
    and common stop words (see :func:`_normalize`).  A ratio equal to or
    above ``threshold`` is considered a potential synonym.  Adjust
    ``threshold`` to tune sensitivity.
    """
    a_norm = _normalize(a)
    b_norm = _normalize(b)
    return difflib.SequenceMatcher(None, a_norm, b_norm).ratio() >= threshold

# Russian stop words and filler words to ignore during normalization
_STOP_WORDS = {
    'при', 'этом', 'с', 'со', 'возможностью', 'возможность', 'встроенным',
    'встроенной', 'встроенное', 'встроенные', 'использует', 'использующий',
    'использующая', 'использование', 'снабжён', 'снабжен', 'снабженный', 'снабжённый',
    'снабженная', 'снабжённая', 'и', 'или', 'для', 'обеспечивает', 'позволяет',
    'при этом', 'при этом'
}


def _normalize(text: str) -> str:
    """Normalize a Russian phrase for comparison.

    This function lowercases the text, removes punctuation, splits into
    words, drops common stop words, and joins back into a normalized
    string.  It is a simple heuristic to aid in semantic matching of
    features; for more robust results one could integrate stemming or
    morphological analysis libraries.
    """
    # Remove punctuation
    import string
    translator = str.maketrans('', '', string.punctuation + '«»"\'–—')
    lower = text.lower().translate(translator)
    # Split words and filter out stop words
    words = [w for w in lower.split() if w not in _STOP_WORDS]
    return ' '.join(words)


def _search_matches(
    feature: str,
    prototypes: List[Union[str, Dict[str, Any]]],
    threshold: float = 0.6,
) -> List[Dict[str, Any]]:
    """Return all matching prototypes for a given feature.

    This helper iterates over the provided prototypes and collects
    matches.  A match is considered **exact** if the lower‑cased feature
    string appears verbatim within the prototype text.  Otherwise, if
    the normalized strings are similar according to :func:`_similar`, the
    match is considered **similar**.  Each match dictionary contains
    ``match_type``, ``prototype`` and ``similarity`` keys.  Results are
    sorted first by match type (exact first) and then by descending
    similarity ratio.  If no matches are found, an empty list is
    returned.

    Parameters
    ----------
    feature:
        The distinctive feature to search for.

    prototypes:
        A list of known patent descriptions.  Elements can be strings or
        dictionaries with ``text`` and an identifier (e.g. ``id`` or
        ``link``).  When a match is returned, the original element is
        included as ``prototype``.

    threshold:
        Minimum similarity ratio for a fuzzy match.  Lowering this value
        increases recall but may introduce false positives.

    Returns
    -------
    List[dict]
        Each element has keys ``match_type`` ("точное совпадение" or
        "похожее"), ``prototype``, and ``similarity`` (ratio).  The list
        is empty if no matches are found.
    """
    feature_norm = _normalize(feature)
    feature_lc = feature.lower()

    def proto_text(proto):
        return proto['text'] if isinstance(proto, dict) else proto

    matches: List[Dict[str, Any]] = []
    for proto in prototypes:
        text = proto_text(proto)
        # Check exact substring match
        if feature_lc in text.lower():
            matches.append({
                "match_type": "точное совпадение",
                "prototype": proto,
                "similarity": 1.0,
            })
        else:
            # Compute similarity ratio on normalized strings
            ratio = difflib.SequenceMatcher(None, feature_norm, _normalize(text)).ratio()
            if ratio >= threshold:
                matches.append({
                    "match_type": "похожее",
                    "prototype": proto,
                    "similarity": ratio,
                })
    # Sort matches: exact matches first, then by similarity descending
    matches.sort(key=lambda m: (0 if m["match_type"] == "точное совпадение" else 1, -m["similarity"]))
    return matches


def _split_features(distinctive: str) -> List[str]:
    """Split a string of distinctive features into individual items.

    Distinctive features are often listed separated by commas, semicolons
    or conjunctions.  This function uses simple heuristics to break the
    string into a list of candidate features.

    Parameters
    ----------
    distinctive:
        The raw distinctive part extracted from the idea description.

    Returns
    -------
    List[str]
        A list of feature strings stripped of leading/trailing whitespace.
    """
    # Replace conjunctions with commas for easier splitting
    # Add commas around conjunctions and nested phrases to better split complex features
    text = distinctive
    # Normalizing certain phrases that indicate additional clauses
    text = text.replace(' и ', ', ')  # split at ' и '
    text = text.replace(';', ',')
    text = text.replace(' при этом ', ', ')  # separate nested clause
    text = text.replace(' с возможностью ', ', с возможностью ')  # ensure comma before possibility
    # After these replacements, split by comma
    parts = [p.strip() for p in text.split(',') if p.strip()]
    return parts


def check_novelty(
    idea: str,
    prototypes: Optional[List[Union[str, Dict[str, Any]]]] = None,
    *,
    similarity_threshold: float = 0.6,
    top_n_matches: Optional[int] = 1,
    search_fn: Optional[
        Callable[[str, List[Union[str, Dict[str, Any]]], float], List[Dict[str, Any]]]
    ] = None,
) -> Dict[str, Any]:
    """Assess the novelty of an invention's distinctive features.

    This function uses :func:`extract_features` to obtain the distinctive
    features from the idea description.  Each feature is compared
    against the provided list of prototype descriptions.  If a feature
    is found verbatim or with high similarity, it is marked as
    "известный".  Otherwise, it is marked as "новый".  The result
    includes a per‑feature status and explanation and an overall
    conclusion on whether the invention appears novel.

    Parameters
    ----------
    idea:
        The free‑form description of the invention.

    prototypes:
        A list of known patent descriptions.  If ``None``, an empty list
        is used.  In a production environment this could be replaced by
        a call to an external patent search API (e.g., Espacenet).

    Parameters
    ----------
    idea:
        The free‑form description of the invention.

    prototypes:
        A list of known patent descriptions.  Each element can be a string or a
        dictionary with keys such as ``text``, ``id`` or ``link``.  When a
        match is returned, the original element is referenced in the
        ``prototype`` field.

    similarity_threshold:
        Base threshold for fuzzy matching; can be adjusted to make the
        comparison more or less strict.  Users may adapt this value for
        specific features by calling the function per feature.

    top_n_matches:
        If ``None``, all matching prototypes are returned for each feature.
        Otherwise only the first ``N`` matches (sorted by match type and
        similarity) are included.  Defaults to ``1``.

    search_fn:
        Optional custom search function.  It must accept a feature string,
        the prototype list and a similarity threshold, and return a list of
        match dictionaries with keys ``match_type``, ``prototype`` and
        ``similarity``.  When provided, this function replaces the
        built‑in search across ``prototypes``; it can be used to query
        external patent APIs such as Espacenet or Google Patents.

    Returns
    -------
    dict
        A dictionary with two keys:

        - ``features``: список словарей, каждый содержит:
            * ``feature`` – текст признака;
            * ``status`` – "известный" или "новый";
            * ``match_type`` – тип совпадения для основного прототипа;
            * ``prototype`` – список идентификаторов или ссылок на найденные прототипы;
            * ``matches`` – подробный список совпадений (каждое с полями ``match_type``, ``prototype``, ``similarity``);
            * ``explanation`` – краткое пояснение, суммирующее совпадения.
        - ``conclusion``: общий вывод о наличии новизны у изобретения.
    """
    prototypes = prototypes or []  # type: ignore
    features_data: List[Dict[str, str]] = []
    extracted = extract_features(idea)
    distinctive = extracted.get('distinctive', '')

    if not distinctive:
        conclusion = (
            "Не удалось выделить отличительные признаки. "
            "Новизну определить невозможно."
        )
        return {"features": features_data, "conclusion": conclusion}

    # Split the distinctive part into individual features
    feature_list = _split_features(distinctive)
    any_new = False
    for feat in feature_list:
        # Use provided search function or the default _search_matches
        search_function = search_fn or _search_matches
        all_matches = search_function(feat, prototypes, threshold=similarity_threshold)
        # Limit the number of matches returned if top_n_matches is specified
        if top_n_matches is not None:
            matches_to_return = all_matches[:top_n_matches]
        else:
            matches_to_return = all_matches

        if matches_to_return:
            status = "известный"
            # Determine primary match type from the first match
            primary_match = matches_to_return[0]
            match_type = primary_match["match_type"]
            # Build explanation summarizing matched prototypes
            expl_parts = []
            for m in matches_to_return:
                proto = m["prototype"]
                mt = m["match_type"]
                # Determine identifier or excerpt
                if isinstance(proto, dict):
                    proto_id = proto.get("id") or proto.get("link") or proto.get("text", "")
                    proto_excerpt = proto.get("text", "")[:100]
                else:
                    proto_id = proto[:100]
                    proto_excerpt = proto[:100]
                expl_parts.append(f"{mt}: '{proto_excerpt}...'")
            explanation = "; ".join(expl_parts)
            prototype_field = [
                (p["prototype"].get("id") if isinstance(p["prototype"], dict) else p["prototype"])
                for p in matches_to_return
            ]
        else:
            status = "новый"
            match_type = "не найдено"
            any_new = True
            explanation = "Признак не найден среди прототипов."
            prototype_field = []
        features_data.append({
            "feature": feat,
            "status": status,
            "match_type": match_type,
            "prototype": prototype_field,
            "matches": matches_to_return,
            "explanation": explanation,
        })

    # Form an overall conclusion
    if any_new:
        conclusion = (
            "Обнаружены новые отличительные признаки — изобретение обладает новизной."
        )
    else:
        conclusion = (
            "Все отличительные признаки соответствуют уровню техники — новизна отсутствует."
        )

    return {"features": features_data, "conclusion": conclusion}


__all__ = ["check_novelty"]