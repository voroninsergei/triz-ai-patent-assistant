"""Drawing mapper module.

This module implements a simple facility to associate patent claim
features with drawing positions.  Given the text of the claims and a
dictionary mapping feature phrases to drawing numbers, the function
:func:`generate_html_report` produces an HTML table listing each
feature and its assigned position.  Any features that do not have a
mapping are highlighted with a warning in the report.

Requirement 2.5 and F4 specify that a report linking claim elements
to drawing positions must be generated in HTML format, and all
positions must be present in the report.  This implementation
generates a minimal HTML file satisfying those conditions.
"""

from __future__ import annotations

import html
from typing import Dict, List

from generate_formula import parse_input, deduplicate_features


def _extract_features_for_mapping(claim_text: str) -> List[str]:
    """Extract unique distinctive features from the independent claim.

    Parameters
    ----------
    claim_text : str
        A patent claim from which to extract features.

    Returns
    -------
    list of str
        A list of distinctive feature phrases after deduplication.
    """
    parts = parse_input(claim_text)
    _, distinctive_dedup, _ = deduplicate_features(parts.get('known', ''), parts.get('distinctive', ''))
    if distinctive_dedup:
        return [f.strip() for f in distinctive_dedup.split(',') if f.strip()]
    return []


def generate_html_report(claim_text: str, mapping: Dict[str, str]) -> str:
    """Generate an HTML report linking claim features to drawing positions.

    Parameters
    ----------
    claim_text : str
        The patent claim text containing the independent claim.
    mapping : dict
        A mapping from feature phrases (as strings) to drawing
        identifiers (e.g., '1', '2a', etc.).  Keys should match the
        distinctive features extracted from the claim.

    Returns
    -------
    str
        A string containing an HTML document with a table showing the
        association between claim features and drawing positions.  Any
        unmapped features will be indicated with a warning.
    """
    features = _extract_features_for_mapping(claim_text)
    rows: List[str] = []
    for feat in features:
        pos = mapping.get(feat)
        if pos:
            rows.append(f"<tr><td>{html.escape(feat)}</td><td>{html.escape(pos)}</td></tr>")
        else:
            rows.append(
                f"<tr><td>{html.escape(feat)}</td><td><em>Нет соответствия</em></td></tr>"
            )
    html_rows = "\n".join(rows)
    html_content = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Сопоставление признаков и чертежей</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>Сопоставление признаков формулы с чертежами</h1>
    <table>
        <thead>
            <tr><th>Признак</th><th>Позиция на чертеже</th></tr>
        </thead>
        <tbody>
            {html_rows}
        </tbody>
    </table>
</body>
</html>
"""
    return html_content