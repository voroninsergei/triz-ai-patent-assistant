"""
TRIZ System Module
===================

This module implements a simple prototype of a system that takes a free‑form
description of an invention and derives useful analytical artefacts:

* **extract_keywords** – identifies the most salient technical terms from
  the input text.  The design document emphasises that keywords should be
  specific, actionable and avoid generic terms or temporary context.  This
  mirrors the guidance in the memory rating prompts, where generic
  information is discarded in favour of specific, actionable preferences【340773968921043†L19-L27】【340773968921043†L63-L69】.

* **classify_ipc** – maps extracted keywords to International Patent
  Classification (IPC) codes.  In a production system this step would call
  an external classifier or patent API; here we use a simple static mapping
  that can easily be extended.

* **map_triz_functions** – associates IPC codes and keywords with TRIZ
  functions.  TRIZ functions describe what a system does (for example,
  *преобразовывать*, *передавать*, *измерять*) and form the basis for
  identifying contradictions.

* **identify_contradictions** – scans the description and keywords for
  potential technical contradictions.  TRIZ distinguishes between
  situations where improving one parameter degrades another (technical
  contradiction) and situations where an element must have mutually
  exclusive properties (physical contradiction).  This implementation
  contains simple heuristics and can be extended with a richer database of
  contradictions.

* **analyze_invention** – orchestrates the process and returns a summary
  containing keywords, IPC codes, TRIZ functions and identified
  contradictions.  It can serve as a building block for downstream
  applications, such as assessing patentability or proposing inventive
  principles.

The mappings used in this module are intentionally simplistic to keep the
demonstration self‑contained.  For real applications you would augment the
mappings with comprehensive tables of IPC classes, TRIZ functions and
contradictions, and replace the heuristics with machine‑learning models or
external API calls.
"""

from __future__ import annotations

import re
import string
from collections import Counter
from typing import Dict, List, Optional, Tuple


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extracts salient keywords from a free‑form description.

    The function uses a simple heuristic: it normalises the text to lower
    case, removes punctuation, splits on whitespace and filters out
    stopwords.  It then selects the most frequent tokens longer than 3
    characters.  In Russian descriptions, many technical terms are nouns
    ending in "‑tion" equivalents or specific domain words, so this
    heuristic captures many of them.  The number of returned keywords can
    be controlled with ``max_keywords``.

    Parameters
    ----------
    text : str
        The invention description.
    max_keywords : int, optional
        Maximum number of keywords to return, by default 10.

    Returns
    -------
    List[str]
        A list of keywords sorted by frequency.
    """
    # Define a simple list of Russian and English stopwords.  In practice
    # consider using a more comprehensive stopword list or NLP library.
    stopwords = {
        # Russian stopwords
        "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как",
        "а", "то", "все", "она", "так", "его", "но", "да", "ты", "к",
        "у", "же", "вы", "за", "бы", "по", "только", "ее", "мне", "было",
        "вот", "от", "меня", "еще", "нет", "о", "из", "ему", "теперь",
        "когда", "даже", "ну", "вдруг", "ли", "если", "уже", "или", "ни",
        "быть", "был", "него", "до", "вас", "нибудь", "опять", "уж", "вам",
        "ведь", "там", "потом", "себя", "ничего", "ей", "может", "они",
        "тут", "где", "есть", "надо", "ней", "для", "мы", "тебя", "их",
        "чем", "была", "сам", "чтоб", "без", "будто", "чего", "раз",
        "тоже", "себе", "под", "будет", "ж", "тогда", "кто", "этот",
        "того", "потому", "этого", "какой", "совсем", "ним", "здесь",
        "этом", "один", "почти", "мой", "тем", "чтобы", "нее", "сейчас",
        "были", "куда", "зачем", "всех", "никогда", "можно", "при",
        "наконец", "два", "об", "другой", "хоть", "после", "над",
        "больше", "тот", "через", "эти", "нас", "про", "всего", "них",
        "какая", "много", "разве", "три", "эту", "моя", "впрочем", "хорошо",
        "свою", "этой", "перед", "иногда", "лучше", "чуть", "том",
        # English stopwords
        "the", "of", "and", "a", "to", "in", "is", "it", "you", "that",
        "he", "was", "for", "on", "are", "with", "as", "I", "his", "they",
        "be", "at", "one", "have", "this", "from", "or", "had", "by",
        "hot", "word", "but", "what", "some", "we", "can", "out", "other",
        "were", "all", "there", "when", "up", "use", "your", "how",
        "said", "an", "each", "she", "which", "their", "if", "will",
        "way", "about", "many", "then", "them", "write", "would", "like",
        "so", "these", "her", "long", "make", "thing", "see", "him", "two",
        "has", "look", "more", "day", "could", "go", "come", "did", "my",
        "sound", "no", "most", "people", "over", "know", "water", "than",
        "call", "first", "who", "may", "down", "side", "been", "now",
        "find"
    }

    # Normalise text: lower case and remove punctuation
    text_clean = text.lower()
    text_clean = text_clean.translate(str.maketrans('', '', string.punctuation))
    tokens = re.split(r"\s+", text_clean)

    # Optionally perform lemmatisation using external library (Yandex mystem or spaCy).
    # If such a library is not available, a simple identity function is used.
    try:
        # Try to import Yandex Mystem
        from pymystem3 import Mystem  # type: ignore
        mystem = Mystem()

        def lemmatize_word(word: str) -> str:
            # Mystem returns list of lemmas; take first lemma and strip whitespace
            res = mystem.lemmatize(word)
            return res[0].strip() if res else word

    except Exception:
        # Fallback: identity function
        def lemmatize_word(word: str) -> str:
            return word

    # Filter tokens: remove stopwords, numbers and short words, and lemmatise
    candidates: List[str] = []
    for t in tokens:
        if not t:
            continue
        if any(c.isdigit() for c in t):
            continue
        if len(t) <= 3:
            continue
        if t in stopwords:
            continue
        # Lemmatise
        lemma = lemmatize_word(t)
        if lemma and lemma not in stopwords and len(lemma) > 3:
            candidates.append(lemma)

    # Count frequency
    freq = Counter(candidates)

    # Select top keywords
    most_common = [word for word, _ in freq.most_common(max_keywords)]
    return most_common


def classify_ipc(keywords: List[str], ipc_mapping: Optional[Dict[str, List[str]]] = None,
                 classifier_fn: Optional[callable] = None) -> List[str]:
    """Classifies keywords into IPC codes.

    This simple implementation uses a static mapping from keywords to IPC
    classes.  If ``ipc_mapping`` is supplied, it overrides the default
    mapping.  The result is a list of unique IPC codes that correspond to
    any of the provided keywords.

    Parameters
    ----------
    keywords : List[str]
        List of extracted keywords.
    ipc_mapping : Dict[str, List[str]], optional
        A custom mapping from keywords to IPC codes.

    Returns
    -------
    List[str]
        A list of IPC codes (strings) deduplicated.
    """
    # Default simplistic mapping.  In a real system this should be
    # comprehensive or replaced by an external classifier.
    default_mapping: Dict[str, List[str]] = {
        # Mechanical engineering keywords
        "машина": ["B60R"],  # vehicles, seatbelts etc.
        "двигатель": ["F02B"],  # internal combustion engines
        "насос": ["F04B"],  # pumps
        "турбина": ["F01D"],  # gas- or steam-turbines
        "компрессор": ["F04D"],
        "передача": ["F16H"],  # gearings
        # Electronics
        "транзистор": ["H01L"],
        "микросхема": ["H01L"],
        "батарея": ["H01M"],  # batteries
        "аккумулятор": ["H01M"],
        # Chemicals
        "катализатор": ["B01J"],
        "полимер": ["C08L"],
        "сплав": ["C22C"],
        # Generic functions
        "очистка": ["B01D"],  # separation
        "фильтрация": ["B01D"],
        "измерение": ["G01D"],  # measuring
        "управление": ["G05B"],  # control
    }
    mapping = ipc_mapping or default_mapping
    ipc_codes: List[str] = []

    # If an external classifier function is provided, defer classification to it.
    if classifier_fn is not None:
        try:
            codes = classifier_fn(keywords)
            # Ensure list
            return list(dict.fromkeys(codes)) if codes else []
        except Exception:
            # Fall back to static mapping on error
            pass

    # Helper to normalise morphological variants for Russian nouns.
    def normalise_word(word: str) -> str:
        suffixes = [
            "ом", "ем", "ам", "ям", "ах", "ях", "ой", "ей", "ий", "ый",
            "ого", "его", "ов", "ев", "ым", "им", "ю", "у", "а", "ы",
            "е", "о", "и", "я"
        ]
        for suff in suffixes:
            if word.endswith(suff) and len(word) > len(suff) + 1:
                return word[:-len(suff)]
        return word

    for kw in keywords:
        codes = mapping.get(kw)
        if not codes:
            # Try normalised form
            base = normalise_word(kw)
            codes = mapping.get(base)
        if codes:
            ipc_codes.extend(codes)
    # Deduplicate while preserving order
    unique_codes = []
    seen = set()
    for code in ipc_codes:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)
    return unique_codes


def map_triz_functions(ipc_codes: List[str], keywords: List[str], triz_mapping: Optional[Dict[str, List[str]]] = None) -> List[str]:
    """Maps IPC codes and keywords to TRIZ functions.

    The TRIZ methodology defines a set of archetypal functions that
    engineering systems perform, such as *передавать* (to transmit),
    *преобразовывать* (to transform), *измерять* (to measure), etc.  This
    function uses a simple mapping from IPC codes and keywords to TRIZ
    functions.  If no mapping is provided, a default small mapping is used.

    Parameters
    ----------
    ipc_codes : List[str]
        List of IPC codes identified for the invention.
    keywords : List[str]
        List of keywords extracted from the invention description.
    triz_mapping : Dict[str, List[str]], optional
        Custom mapping from IPC codes or keywords to TRIZ functions.

    Returns
    -------
    List[str]
        A deduplicated list of TRIZ functions.
    """
    default_triz_map: Dict[str, List[str]] = {
        # IPC codes
        "B60R": ["передавать движение", "удерживать"],
        "F02B": ["преобразовывать энергию", "поджигать топливо"],
        "F04B": ["перекачивать", "создавать давление"],
        "F01D": ["преобразовывать энергию", "увеличивать скорость"],
        "F04D": ["создавать поток", "сжимать"],
        "F16H": ["передавать энергию", "переводить движение"],
        "H01L": ["управлять током", "усиливать сигнал"],
        "H01M": ["накапливать энергию", "выделять энергию"],
        "B01J": ["ускорять реакцию", "очищать"],
        "C08L": ["создавать материал", "модифицировать свойства"],
        "C22C": ["создавать материал", "улучшать свойства"],
        "B01D": ["очищать", "разделять"],
        "G01D": ["измерять", "контролировать"],
        "G05B": ["управлять", "регулировать"],
        # Keywords directly
        "очистка": ["разделять", "избавляться от загрязнений"],
        "измерение": ["определять параметр"],
        "управление": ["регулировать"],
        "фильтрация": ["отделять", "очищать"],
        "батарея": ["накапливать энергию", "отдавать энергию"],
    }
    mapping = triz_mapping or default_triz_map
    functions: List[str] = []
    # First map based on IPC codes
    for code in ipc_codes:
        if code in mapping:
            functions.extend(mapping[code])
    # Then map based on keywords
    # Helper to normalise morphological variants
    def normalise_word(word: str) -> str:
        suffixes = [
            "ом", "ем", "ам", "ям", "ах", "ях", "ой", "ей", "ий", "ый",
            "ого", "его", "ов", "ев", "ым", "им", "ю", "у", "а", "ы",
            "е", "о", "и", "я"
        ]
        for suff in suffixes:
            if word.endswith(suff) and len(word) > len(suff) + 1:
                return word[:-len(suff)]
        return word

    for kw in keywords:
        funcs = mapping.get(kw)
        if not funcs:
            base = normalise_word(kw)
            funcs = mapping.get(base)
        if funcs:
            functions.extend(funcs)
    # Deduplicate
    seen = set()
    unique_funcs = []
    for f in functions:
        if f not in seen:
            seen.add(f)
            unique_funcs.append(f)
    return unique_funcs


def identify_contradictions(text: str, keywords: List[str]) -> List[Dict[str, str]]:
    """Identifies possible TRIZ contradictions in the description.

    This heuristic implementation looks for phrases that hint at improving
    one parameter at the cost of another or requiring mutually exclusive
    properties.  For example, if the description contains words like
    "увеличить" and "уменьшить" close together, it might indicate a
    technical contradiction.  If a sentence mentions opposite adjectives
    applied to the same object (e.g., "жесткий" and "гибкий"), a physical
    contradiction is suspected.

    Parameters
    ----------
    text : str
        The invention description.
    keywords : List[str]
        List of extracted keywords used to focus contradiction detection.

    Returns
    -------
    List[Dict[str, str]]
        A list of dictionaries describing each contradiction with keys:
        "type" (technical/physical), "description" (human‑readable text).
    """
    contradictions: List[Dict[str, str]] = []
    # Technical contradictions: look for patterns of improvement and worsening
    improvement_words = {"увеличить", "улучшить", "повысить", "снизить"}
    deterioration_words = {"уменьшить", "снизить", "ухудшить"}
    # Search in sentences
    sentences = re.split(r"(?<=[.!?])\s+", text)
    for sent in sentences:
        s_lower = sent.lower()
        for imp in improvement_words:
            for det in deterioration_words:
                if imp in s_lower and det in s_lower:
                    contradictions.append({
                        "type": "technical",
                        "description": f"В предложении '{sent.strip()}' улучшение ('{imp}') сочетается с ухудшением ('{det}')."
                    })
                    break
            else:
                continue
            break
        # Physical contradictions: look for opposite adjectives
        opposite_pairs = [
            ("жесткий", "гибкий"),
            ("горячий", "холодный"),
            ("легкий", "тяжелый"),
            ("прочность", "хрупкость"),
            ("быстрый", "медленный"),
            ("большой", "маленький"),
            ("сильный", "слабый"),
            ("плотный", "разреженный"),
            ("твердый", "мягкий"),
            ("густой", "жидкий"),
            ("дешевый", "дорогой"),
            ("короткий", "длинный"),
            ("гладкий", "шероховатый"),
        ]
        for a, b in opposite_pairs:
            if a in s_lower and b in s_lower:
                contradictions.append({
                    "type": "physical",
                    "description": f"В предложении '{sent.strip()}' упомянуты противоположные свойства '{a}' и '{b}'."
                })

        # Heuristic: common engineering contradictions like "легкий и прочный"
        if "легк" in s_lower and "прочн" in s_lower:
            contradictions.append({
                "type": "physical",
                "description": f"В предложении '{sent.strip()}' описана необходимость сочетать лёгкость и прочность." 
            })
    return contradictions


def analyze_invention(text: str, ipc_mapping: Optional[Dict[str, List[str]]] = None,
                      triz_mapping: Optional[Dict[str, List[str]]] = None,
                      max_keywords: int = 10) -> Dict[str, object]:
    """Analyzes an invention description and returns TRIZ‑related artefacts.

    Parameters
    ----------
    text : str
        The invention description.
    ipc_mapping : Dict[str, List[str]], optional
        Custom mapping for IPC classification.
    triz_mapping : Dict[str, List[str]], optional
        Custom mapping for TRIZ function assignment.
    max_keywords : int, optional
        Maximum number of keywords to extract.

    Returns
    -------
    Dict[str, object]
        A dictionary containing:
        * "keywords" – list of extracted keywords;
        * "ipc_codes" – list of IPC codes;
        * "triz_functions" – list of TRIZ functions;
        * "contradictions" – list of contradiction descriptions.
    """
    keywords = extract_keywords(text, max_keywords=max_keywords)
    ipc_codes = classify_ipc(keywords, ipc_mapping=ipc_mapping)
    triz_functions = map_triz_functions(ipc_codes, keywords, triz_mapping=triz_mapping)
    contradictions = identify_contradictions(text, keywords)
    return {
        "keywords": keywords,
        "ipc_codes": ipc_codes,
        "triz_functions": triz_functions,
        "contradictions": contradictions,
    }


def export_report(analysis: Dict[str, object], filename: str) -> None:
    """Exports analysis results to a simple .docx file with a table.

    The generated document contains a table with four columns:
    "Keyword", "IPC", "TRIZ functions" and "Contradictions".  Each row
    corresponds to one keyword from the analysis.  IPC codes and TRIZ
    functions are joined with commas, contradictions are joined with
    semicolons.  If there are more keywords than contradictions, the
    contradiction column is filled only for the first row.  The file is
    saved at the provided ``filename`` path.

    Parameters
    ----------
    analysis : dict
        The result of ``analyze_invention``.
    filename : str or file-like object
        Path to the output .docx file or a binary file-like object.  When
        passing a file-like object (e.g. ``io.BytesIO``), the report is
        written into that buffer.  If a string path is provided, it should
        end with ``.docx``.
    """
    from zipfile import ZipFile, ZIP_DEFLATED
    import os

    keywords: List[str] = analysis.get("keywords", [])  # type: ignore
    ipc_codes: List[str] = analysis.get("ipc_codes", [])  # type: ignore
    triz_functions: List[str] = analysis.get("triz_functions", [])  # type: ignore
    contradictions: List[Dict[str, str]] = analysis.get("contradictions", [])  # type: ignore
    # Build rows: each keyword uses same IPC codes and TRIZ functions
    rows: List[List[str]] = []
    contr_desc = "; ".join([c["description"] for c in contradictions])
    for i, kw in enumerate(keywords):
        row = [
            kw,
            ", ".join(ipc_codes) if ipc_codes else "",
            ", ".join(triz_functions) if triz_functions else "",
            contr_desc if i == 0 else "",
        ]
        rows.append(row)
    # WordprocessingML namespace
    def w(tag: str) -> str:
        return f"w:{tag}"
    # Build document.xml content
    doc_lines: List[str] = []
    doc_lines.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    doc_lines.append('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" ')
    doc_lines.append(' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">')
    doc_lines.append('  <w:body>')
    # Table start
    doc_lines.append('    <w:tbl>')
    # Table grid: four equal columns
    doc_lines.append('      <w:tblGrid>')
    for _ in range(4):
        doc_lines.append('        <w:gridCol w:w="2500"/>')
    doc_lines.append('      </w:tblGrid>')
    # Header row
    headers = ["Ключевое слово", "IPC", "TRIZ‑функции", "Противоречия"]
    doc_lines.append('      <w:tr>')
    for h in headers:
        doc_lines.append('        <w:tc><w:tcPr/><w:p><w:r><w:t>{}</w:t></w:r></w:p></w:tc>'.format(h))
    doc_lines.append('      </w:tr>')
    # Data rows
    for row in rows:
        doc_lines.append('      <w:tr>')
        for cell in row:
            text = cell.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            doc_lines.append('        <w:tc><w:tcPr/><w:p><w:r><w:t>{}</w:t></w:r></w:p></w:tc>'.format(text))
        doc_lines.append('      </w:tr>')
    doc_lines.append('    </w:tbl>')
    # End body
    doc_lines.append('    <w:sectPr/>')
    doc_lines.append('  </w:body>')
    doc_lines.append('</w:document>')
    document_xml = "\n".join(doc_lines)
    # Build [Content_Types].xml
    ct_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
    # Build _rels/.rels
    rels_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="R1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    # Prepare directories inside zip
    # Determine if filename is a path or a file-like object
    # If it's a string or Path, we open a new ZipFile; if it's a file-like,
    # we wrap it into ZipFile directly.
    if hasattr(filename, 'write'):
        # File-like object
        zf = ZipFile(filename, 'w', ZIP_DEFLATED)
        # Write contents
        zf.writestr('[Content_Types].xml', ct_xml)
        zf.writestr('_rels/.rels', rels_xml)
        zf.writestr('word/document.xml', document_xml)
        zf.close()
    else:
        with ZipFile(filename, 'w', ZIP_DEFLATED) as zf:
            # Content types
            zf.writestr('[Content_Types].xml', ct_xml)
            # Relationships
            zf.writestr('_rels/.rels', rels_xml)
            # Document
            zf.writestr('word/document.xml', document_xml)
    # Done