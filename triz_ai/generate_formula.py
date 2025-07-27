"""
Utility functions for generating the first claim of a patent from an idea description.

This module exposes a single function, ``generate_formula``, which takes a
textual description of an invention and attempts to construct the first
independent claim (claim 1) following typical patent‑claim structure in
Russian practice.  The function tries to extract the title, known
features (ограничительная часть), distinctive features (отличительная
часть) and the intended effect or ideal final result (ИКР) from the
description.  It then assembles these segments into a single sentence
using the canonical “отличающийся тем, что …” phrase to separate the
restrictive and distinctive parts.

The heuristics implemented here are simplistic and rely on keyword
searches.  They are not a substitute for a professional patent
attorney.  Nevertheless, they can help convert informal ideas into a
formal‑sounding claim that follows the guidelines outlined in
OpenPatent's documentation and common patent drafting practice.

Usage::

    from generate_formula import generate_formula

    # Compose the idea description using single quotes to avoid ending the
    # docstring prematurely.  Newlines separate labeled sections.
    idea_text = (
        'Название: Устройство для очистки воды\n'
        'Известные признаки: содержит корпус и фильтрующий элемент\n'
        'Отличительные признаки: снабжён встроенным ультрафиолетовым излучателем\n'
        'Эффект: обеспечивает обеззараживание воды'
    )
    claim = generate_formula(idea_text)
    print(claim)

"""

import re
from typing import List, Optional

def _extract_section(text: str, markers: List[str]) -> Optional[str]:
    """Return the first substring in ``text`` that follows any of the given
    markers.

    Parameters
    ----------
    text:
        The input text where sections may be denoted by labels such as
        ``"Название"`` or ``"Известные признаки"``.  Section markers
        should be case insensitive.

    markers:
        A list of substrings (markers) that identify the start of a
        section.  If a marker appears in a line, the function will
        return the remainder of that line after the marker and any
        punctuation following it.

    Returns
    -------
    Optional[str]
        The extracted section text, or ``None`` if no markers were found.
    """
    for line in text.splitlines():
        lower = line.lower()
        for marker in markers:
            if marker in lower:
                # locate the marker in the lowercased line
                start_idx = lower.find(marker) + len(marker)
                # strip punctuation and whitespace after the marker
                return line[start_idx:].strip(" :–-\t")
    return None


def _collect_sentences(text: str, markers: List[str]) -> str:
    """Collect sentences from ``text`` containing any of the given markers.

    The function splits the text into sentences using a regular expression
    and returns a string made by joining all sentences that contain one
    of the provided keywords (case insensitive).

    Parameters
    ----------
    text:
        The input description from which to extract sentences.

    markers:
        A list of substrings that signal sentences belonging to a
        particular section (e.g., known features or effect).

    Returns
    -------
    str
        All matching sentences concatenated with spaces.  If no
        sentences match, an empty string is returned.
    """
    # Split by sentence terminators followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text)
    selected = []
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(marker in s_lower for marker in markers):
            selected.append(sentence.strip())
    return ' '.join(selected)


# ----------------------------------------------------------------------------
# New pipeline‑based implementation of claim generation
#
# To support the expanded requirements laid out in version 2.0 of the
# technical specification, the original monolithic :func:`generate_formula`
# has been refactored into several helper functions: ``parse_input``,
# ``deduplicate_features`` and ``build_formula``.  These helpers perform
# explicit parsing of the input description, remove duplicate features
# (including simple morphological variants) and assemble the final claim.
# The public ``generate_formula`` function retains backward compatibility:
# it accepts a single string argument as before and returns a plain string
# when called without additional parameters.  When invoked with the
# optional ``style``, ``variants`` or ``language`` parameters it can
# produce more compact or verbose claims and even multiple variants (wide
# and narrow) as a list.  See the docstring of ``generate_formula`` below
# for details.

import logging
import time
from typing import Dict, Tuple, Union, Literal, List as _List, Optional as _Optional

logger = logging.getLogger(__name__)


def parse_input(idea: str, language: str = "ru") -> Dict[str, str]:
    """Parse a free‑form description into its structural parts.

    This helper extracts the title (``name``), known features (``known``),
    distinctive features (``distinctive``) and the intended effect (``effect``)
    from the given description.  It first looks for explicit section labels
    such as "Название" or "Известные признаки"; if none are found, it falls
    back to heuristics similar to the original implementation.

    Parameters
    ----------
    idea:
        A textual description of the invention.  It may contain labelled
        sections separated by newlines or be purely free‑form.
    language:
        The language code (``"ru"`` for Russian or ``"en"`` for English).

    Returns
    -------
    dict
        A dictionary with keys ``name``, ``known``, ``distinctive`` and
        ``effect``.  Missing fields are returned as empty strings.
    """
    clean_text = (idea or "").strip()
    if not clean_text:
        return {"name": "", "known": "", "distinctive": "", "effect": ""}

    # Explicit labels (case insensitive)
    name = _extract_section(clean_text, ['название', 'заголовок', 'имя'])
    known = _extract_section(clean_text, ['известные признаки', 'известные', 'прототип'])
    distinctive = _extract_section(clean_text, ['отличительные признаки', 'отличительные', 'новые признаки'])
    effect = _extract_section(clean_text, ['эффект', 'результат', 'икр', 'идеальный конечный результат'])

    # Heuristic fallbacks if sections are missing
    if not name:
        # Use first non‑empty line as title
        for line in clean_text.splitlines():
            stripped = line.strip()
            if stripped:
                name = stripped
                break
    if not known:
        known = _collect_sentences(clean_text, ['известн', 'прототип', 'существующ'])
    if not distinctive:
        distinctive = _collect_sentences(clean_text, ['нов', 'отлич', 'предлагаем', 'характериз'])
    if not effect:
        effect = _collect_sentences(clean_text, ['эффект', 'результат', 'обеспеч', 'позволя'])

    return {
        "name": (name or "").strip(),
        "known": (known or "").strip(),
        "distinctive": (distinctive or "").strip(),
        "effect": (effect or "").strip(),
    }


def _split_features(features: str) -> _List[str]:
    """Split a raw features string into individual feature phrases.

    This helper normalises separators (commas, conjunctions and semicolons),
    strips trailing punctuation and removes leading verbs such as
    "содержит", "имеет" or "включает".  The resulting list contains
    candidate phrases describing individual features.

    Parameters
    ----------
    features:
        A string containing a comma‑ or conjunction‑separated list of
        features.  May be empty.

    Returns
    -------
    List[str]
        A list of clean feature phrases, with no empty items.
    """
    if not features:
        return []
    # Normalise conjunctions to commas (e.g., " и ", " или ")
    normalised = re.sub(r"\s+(и|или|а также)\s+", ", ", features, flags=re.IGNORECASE)
    # Replace semicolons with commas
    normalised = normalised.replace(';', ',')
    # Remove trailing periods
    normalised = normalised.replace('.', '')
    # Split on comma
    raw_phrases = [p.strip() for p in normalised.split(',') if p.strip()]
    # List of verbs/adjectives to strip from the beginning of phrases
    verbs = {
        'содержит', 'содержат', 'имеет', 'имеют', 'включает', 'включают',
        'включающий', 'включающая', 'включающее', 'включающие',
        'снабжен', 'снабжён', 'снабжена', 'снабжено', 'снабженные',
        'использование', 'использует', 'используют', 'использующий',
        'оснащен', 'оснащена', 'оснащено', 'оснащены', 'управляющий',
        'управляющая', 'управляющее', 'управляющие', 'предусматривает',
        'предусмотрен', 'предусмотрена', 'предусмотрено'
    }
    cleaned: _List[str] = []
    for phrase in raw_phrases:
        words = phrase.split()
        # Remove leading verbs/adjectives
        while words and words[0].lower().strip('.,;:') in verbs:
            words.pop(0)
        cleaned_phrase = ' '.join(words).strip()
        if cleaned_phrase:
            cleaned.append(cleaned_phrase)
    return cleaned


# Attempt to import NLTK's SnowballStemmer for simple stemming.  Fall back to identity.
try:
    from nltk.stem.snowball import SnowballStemmer  # type: ignore

    _RU_STEMMER = SnowballStemmer('russian')
    _EN_STEMMER = SnowballStemmer('english')

    def _stem(word: str, lang: str) -> str:
        word_l = word.lower().strip()
        if not word_l:
            return word_l
        try:
            if lang == 'ru':
                return _RU_STEMMER.stem(word_l)
            else:
                return _EN_STEMMER.stem(word_l)
        except Exception:
            return word_l
except Exception:
    # Fallback: return lowercased word unchanged
    def _stem(word: str, lang: str) -> str:
        return word.lower().strip()


def deduplicate_features(known: str, distinctive: str, language: str = "ru") -> Tuple[str, str, float]:
    """Remove duplicate feature phrases across known and distinctive parts.

    The function splits both the ``known`` and ``distinctive`` feature strings
    into lists of individual phrases, removes redundant entries (those whose
    set of stems is a subset of stems already seen) and ensures that
    distinctive features are truly new relative to the known features.  It
    returns the deduplicated feature strings along with a duplicate
    elimination rate, expressed as a percentage of removed items.

    Parameters
    ----------
    known, distinctive:
        Raw feature strings extracted from the description.  They may be
        empty or contain comma‑ and conjunction‑separated phrases.
    language:
        The language code to select an appropriate stemmer.

    Returns
    -------
    Tuple[str, str, float]
        A tuple containing the deduplicated known features string, the
        deduplicated distinctive features string and the duplicate rate
        (percentage of removed phrases).  The returned strings are
        comma‑separated lists without leading verbs.
    """
    # Split into individual phrases
    known_phrases = _split_features(known)
    distinctive_phrases = _split_features(distinctive)
    total_original = len(known_phrases) + len(distinctive_phrases)
    duplicates_removed = 0

    # Accumulate stems of all accepted known features
    known_accum_stems: set[str] = set()
    dedup_known: _List[str] = []
    for phrase in known_phrases:
        # Compute stem set for the phrase
        stems = { _stem(tok, language) for tok in re.split(r"[\s\-]+", phrase) if tok }
        # If all stems already seen, skip as duplicate
        if stems and stems.issubset(known_accum_stems):
            duplicates_removed += 1
            continue
        dedup_known.append(phrase)
        known_accum_stems.update(stems)

    # Deduplicate distinctive features; ensure they don't duplicate known features
    dedup_distinctive: _List[str] = []
    distinct_accum_stems: set[str] = set()
    for phrase in distinctive_phrases:
        stems = { _stem(tok, language) for tok in re.split(r"[\s\-]+", phrase) if tok }
        # Skip if all stems are already in known stems (pure duplicate)
        if stems and stems.issubset(known_accum_stems):
            duplicates_removed += 1
            continue
        # Skip if duplicate within distinctive
        if stems and stems.issubset(known_accum_stems.union(distinct_accum_stems)):
            duplicates_removed += 1
            continue
        dedup_distinctive.append(phrase)
        distinct_accum_stems.update(stems)

    dup_rate = (duplicates_removed / total_original * 100.0) if total_original else 0.0
    # Join back into comma‑separated strings
    known_str = ', '.join(dedup_known).strip()
    distinctive_str = ', '.join(dedup_distinctive).strip()
    return known_str, distinctive_str, dup_rate


def build_formula(name: str, known: str, distinctive: str, effect: str, language: str = "ru") -> str:
    """Assemble the patent claim from its parts.

    The claim is constructed as a single sentence in the following order:
    ``name`` (title), optionally followed by "включающий " and the list of
    known features, the canonical phrase "отличающийся тем, что" and the
    list of distinctive features, and finally a single occurrence of the
    effect prefixed by "обеспечивает".  Punctuation is added as needed
    and the sentence always ends with a period.

    Parameters
    ----------
    name : str
        The title of the invention.
    known : str
        Comma‑separated known features (may be empty).
    distinctive : str
        Comma‑separated distinctive features (may be empty).
    effect : str
        The intended effect (may be empty).  Any leading "обеспечивает"
        in this string will be removed.
    language : str
        Language code (currently unused but reserved for future localisation).

    Returns
    -------
    str
        The assembled claim as a single sentence.
    """
    parts: _List[str] = []
    # Clean the name: strip trailing punctuation
    name_clean = (name or '').strip().rstrip('.')
    # Always start with the name if present
    if name_clean:
        if known:
            parts.append(f"{name_clean}, включающий {known}")
        else:
            parts.append(name_clean)
    else:
        if known:
            parts.append(f"включающий {known}")
    if distinctive:
        parts.append(f"отличающийся тем, что {distinctive}")
    # Process effect: remove leading trigger words
    effect_clean = (effect or '').strip()
    if effect_clean:
        # Remove existing "обеспечивает" or "provides" at the start
        effect_clean = re.sub(r'^\s*(обеспечивает|provides)\s+', '', effect_clean, flags=re.IGNORECASE)
        effect_clean = effect_clean.rstrip('.')
        parts.append(f"обеспечивает {effect_clean}")
    # Join parts with commas
    formula = ', '.join([p.strip() for p in parts if p.strip()])
    formula = formula.strip()
    if formula and not formula.endswith('.'):
        formula += '.'
    return formula


def _generate_formula_original(idea: str) -> str:
    """Original monolithic implementation preserved for verbose mode.

    This function replicates the behaviour of the pre‑2.0 version of
    :func:`generate_formula`.  It is used internally when the caller
    requests the ``"verbose"`` style to maintain backward compatibility.
    The logic has not been altered except for minor refactoring of
    variable names.

    Parameters
    ----------
    idea : str
        The invention description.

    Returns
    -------
    str
        The generated claim as a single sentence.
    """
    clean_text = (idea or "").strip()
    if not clean_text:
        return ""
    name = _extract_section(clean_text, ['название', 'заголовок', 'имя'])
    known = _extract_section(clean_text, ['известные признаки', 'известные', 'прототип'])
    distinctive = _extract_section(clean_text, ['отличительные признаки', 'отличительные', 'новые признаки'])
    effect = _extract_section(clean_text, ['эффект', 'результат', 'икр', 'идеальный конечный результат'])
    if not name:
        for line in clean_text.splitlines():
            stripped = line.strip()
            if stripped:
                name = stripped
                break
    if not known:
        known = _collect_sentences(clean_text, ['известн', 'прототип', 'существующ'])
    if not distinctive:
        distinctive = _collect_sentences(clean_text, ['нов', 'отлич', 'предлагаем', 'характериз'])
    if not effect:
        effect = _collect_sentences(clean_text, ['эффект', 'результат', 'обеспеч', 'позволя'])
    parts: _List[str] = []
    if name and known:
        parts.append(f"{name}, включающий {known}")
    elif name:
        parts.append(name)
    if distinctive:
        parts.append(f"отличающийся тем, что {distinctive}")
    if effect:
        parts.append(f"обеспечивает {effect}")
    formula = ', '.join([p for p in parts if p]).strip()
    if formula and not formula.endswith('.'):
        formula += '.'
    return formula


def generate_formula(title: str,
                     known: str = "",
                     distinct: str = "",
                     effect: str = "",
                     variants: int | str | None = None) -> str:
    # 👉 кастуем к int, если это строка
    if variants is not None:
        try:
            variants = int(variants)
        except ValueError:
            variants = None          # или 1 – как вам логичнее

    if variants is None or variants <= 1:
        # Return a single string for backward compatibility
        return wide_formula

    # Build the narrow claim using original features without deduplication
    narrow_formula = build_formula(
        parts.get('name', ''),
        parts.get('known', ''),
        parts.get('distinctive', ''),
        parts.get('effect', ''),
        language=language,
    )
    # Compose the list of variants: first wide, then narrow, then repeat wide if more requested
    formulas: _List[str] = [wide_formula, narrow_formula]
    if variants > 2:
        formulas.extend([wide_formula] * (variants - 2))
    return formulas


def extract_features(idea: str) -> dict:
    """Extract structural parts of an idea description for downstream analysis.

    This helper parses the same sections used by :func:`generate_formula` but
    returns them as a dictionary rather than assembling them into a single
    sentence.  It exposes the title (``name``), known features (``known``),
    distinctive features (``distinctive``) and the intended effect (``effect``).
    These parts can then be passed to other components, such as a model
    evaluating the non‑obviousness of the distinctive features.

    Parameters
    ----------
    idea:
        A string describing the invention.  It may contain labeled
        sections or just a free‑form description.

    Returns
    -------
    dict
        A dictionary with keys ``name``, ``known``, ``distinctive``, ``effect``.
        Missing sections are returned as an empty string.  Whitespace is
        trimmed.
    """
    clean_text = (idea or "").strip()
    if not clean_text:
        return {"name": "", "known": "", "distinctive": "", "effect": ""}

    # Reuse the same extraction logic as generate_formula
    name = _extract_section(clean_text, ['название', 'заголовок', 'имя'])
    known = _extract_section(clean_text, ['известные признаки', 'известные', 'прототип'])
    distinctive = _extract_section(clean_text, ['отличительные признаки', 'отличительные', 'новые признаки'])
    effect = _extract_section(clean_text, ['эффект', 'результат', 'икр', 'идеальный конечный результат'])

    # Heuristic fallbacks
    if not name:
        for line in clean_text.splitlines():
            stripped = line.strip()
            if stripped:
                name = stripped
                break
    if not known:
        known = _collect_sentences(clean_text, ['известн', 'прототип', 'существующ'])
    if not distinctive:
        distinctive = _collect_sentences(clean_text, ['нов', 'отлич', 'предлагаем', 'характериз'])
    if not effect:
        effect = _collect_sentences(clean_text, ['эффект', 'результат', 'обеспеч', 'позволя'])

    return {
        "name": (name or "").strip(),
        "known": (known or "").strip(),
        "distinctive": (distinctive or "").strip(),
        "effect": (effect or "").strip(),
    }


__all__ = ["generate_formula", "extract_features"]
