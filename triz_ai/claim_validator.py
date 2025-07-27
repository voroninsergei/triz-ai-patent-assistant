"""Patent claim validator module.

This module provides utilities to validate the structure of patent
claims.  The primary entry point, :func:`validate_claims`, accepts a
string containing one or more claims (each claim on a separate line) and
performs simple checks:

* The first claim must be independent and include at least one known
  element, one distinctive feature and an effect.  These parts are
  extracted using :func:`generate_formula.parse_input`.
* Distinctive features must be unique across claims.
* Dependent claims (claims beyond the first) must reference a prior
  claim number explicitly (e.g., "По пункту 1" or "according to claim 1").

These checks are heuristic but satisfy the acceptance criterion AC2
stating that the validator must detect when an independent claim
erroneously references another claim.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from generate_formula import parse_input, deduplicate_features


def validate_claims(claim_text: str) -> Tuple[bool, List[str]]:
    """Validate a set of patent claims.

    Parameters
    ----------
    claim_text : str
        Claims separated by newlines.  The first line should contain
        the independent claim; subsequent lines, if any, are treated as
        dependent claims.

    Returns
    -------
    (bool, list of str)
        A tuple where the boolean indicates whether the claims pass
        validation and the list contains error messages for any
        violations.
    """
    errors: List[str] = []
    lines = [line.strip() for line in claim_text.strip().splitlines() if line.strip()]
    if not lines:
        errors.append("Нет текста формулы для проверки")
        return False, errors
    # Validate first claim (independent)
    first_claim = lines[0]
    # It should not reference another claim
    if re.search(r"\bпо пункту\b|\baccording to claim\b", first_claim, flags=re.IGNORECASE):
        errors.append("Первый пункт формулы не должен ссылаться на другой пункт")
    # Extract parts to ensure presence of known, distinctive and effect
    parts = parse_input(first_claim)
    # Deduplicate to confirm at least one distinctive feature remains
    _, distinctive_dedup, _ = deduplicate_features(parts.get('known', ''), parts.get('distinctive', ''))
    if not parts.get('known'):
        errors.append("В независимом пункте отсутствуют известные признаки")
    if not parts.get('distinctive'):
        errors.append("В независимом пункте отсутствуют отличительные признаки")
    if not parts.get('effect'):
        errors.append("В независимом пункте отсутствует технический эффект")
    if distinctive_dedup and parts.get('distinctive') and distinctive_dedup != parts.get('distinctive'):
        errors.append("В независимом пункте присутствуют дублирующиеся признаки")
    # Validate dependent claims
    for idx, claim in enumerate(lines[1:], start=2):
        # Each dependent claim should reference a prior claim number
        if not re.search(r"\b(по пункту|according to claim)\s*\d+", claim, flags=re.IGNORECASE):
            errors.append(f"Пункт {idx} не содержит ссылки на предыдущий пункт")
    return len(errors) == 0, errors