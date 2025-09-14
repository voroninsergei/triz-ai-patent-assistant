# -*- coding: utf-8 -*-
import re
from typing import Dict, List as _List

def _norm_lang(language: str) -> str:
    s = (language or "ru").strip().lower()
    # Robust normalization
    if s in {"en", "eng", "english", "en-us", "en_uk", "en-gb", "en-gb"}:
        return "en"
    return "ru"

def _clean_text(s: str) -> str:
    return (s or "").replace("\r", "").strip()

def _extract_section(text: str, labels: _List[str]) -> str:
    # Finds "Label: ..." sections; case-insensitive
    pattern = r"(?im)^(?:{labels})\s*[:：]\s*(.+?)(?=\n[A-Za-zА-Яа-яЁё# ]+[:：]|\Z)"
    re_pat = pattern.format(labels="|".join([re.escape(l) for l in labels]))
    m = re.search(re_pat, text)
    return m.group(1).strip() if m else ""

def _collect_sentences(text: str, markers: _List[str]) -> str:
    parts = re.split(r"(?<=[\.\!\?])\s+", text)
    selected = [sent.strip() for sent in parts if any(re.search(rf"{re.escape(m)}", sent, re.IGNORECASE) for m in markers)]
    return " ".join(selected).strip()

def parse_input(idea: str, language: str = "ru") -> Dict[str, str]:
    clean_text = _clean_text(idea)
    lang = _norm_lang(language)
    if lang == "en":
        name = _extract_section(clean_text, ['title', 'name'])
        known = _extract_section(clean_text, ['known features', 'known', 'prior art', 'existing'])
        distinctive = _extract_section(clean_text, ['distinctive features', 'novel features', 'characterising features', 'wherein'])
        effect = _extract_section(clean_text, ['effect', 'result', 'advantage', 'technical effect', 'benefit'])
    else:
        name = _extract_section(clean_text, ['название', 'заголовок', 'имя'])
        known = _extract_section(clean_text, ['известные признаки', 'известные', 'прототип'])
        distinctive = _extract_section(clean_text, ['отличительные признаки', 'отличительные', 'новые признаки'])
        effect = _extract_section(clean_text, ['эффект', 'результат', 'икр', 'идеальный конечный результат'])

    if not known:
        known = _collect_sentences(clean_text, (['known', 'prior art', 'existing'] if lang == 'en' else ['известн', 'прототип', 'существующ']))
    if not distinctive:
        distinctive = _collect_sentences(clean_text, (['novel', 'distinctive', 'characteris', 'wherein', 'propos'] if lang == 'en' else ['нов', 'отлич', 'предлагаем', 'характериз']))
    if not effect:
        effect = _collect_sentences(clean_text, (['effect', 'result', 'advantage', 'provides', 'whereby'] if lang == 'en' else ['эффект', 'результат', 'обеспеч', 'позволя']))
    return {"name": name, "known": known, "distinctive": distinctive, "effect": effect, "lang": lang}

def _split_features(features: str) -> _List[str]:
    features = (features or "").strip()
    if not features:
        return []
    # RU + EN conjunctions
    normalised = re.sub(r"\s+(и|или|а также|and|or|as well as)\s+", ", ", features, flags=re.IGNORECASE)
    chunks = re.split(r"[,\n;]+", normalised)
    verbs = {
        # RU
        'содержит', 'содержат', 'имеет', 'имеют', 'включает', 'включают',
        'включающий', 'включающая', 'включающее', 'включающие',
        'снабжен', 'снабжён', 'снабжена', 'снабжено', 'снабженные',
        'использование', 'использует', 'используют', 'использующий',
        'оснащен', 'оснащена', 'оснащено', 'оснащены', 'управляющий',
        'управляющая', 'управляющее', 'управляющие', 'предусматривает',
        'предусмотрен', 'предусмотрена', 'предусмотрено',
        # EN
        'comprising', 'comprises', 'include', 'includes', 'including',
        'has', 'having', 'is', 'provided', 'configured', 'adapted',
        'further', 'comprise', 'comprising:', 'including:'
    }
    cleaned = []
    for ch in chunks:
        tok = ch.strip().strip(".").strip()
        tok = re.sub(r"^\b(" + "|".join(sorted(verbs)) + r")\b\s*", "", tok, flags=re.IGNORECASE)
        if tok:
            cleaned.append(tok)
    # de-dup
    seen = set(); out = []
    for x in cleaned:
        k = x.lower()
        if k not in seen:
            out.append(x); seen.add(k)
    return out

def build_formula(name: str, known: str, distinctive: str, effect: str, language: str = "ru") -> str:
    parts: _List[str] = []
    name_clean = (name or '').strip().rstrip('.')
    lang = _norm_lang(language)
    if lang == "en":
        if name_clean and known:
            parts.append(f"{name_clean}, comprising {known}")
        elif name_clean:
            parts.append(name_clean)
        elif known:
            parts.append(f"Comprising {known}")
        if distinctive:
            parts.append(f"wherein {distinctive}")
        effect_clean = (effect or '').strip()
        if effect_clean:
            effect_clean = re.sub(r'^\s*(provides|whereby)\s+', '', effect_clean, flags=re.IGNORECASE).rstrip('.')
            if effect_clean:
                parts.append(f"provides {effect_clean}")
    else:
        if name_clean and known:
            parts.append(f"{name_clean}, включающий {known}")
        elif name_clean:
            parts.append(name_clean)
        elif known:
            parts.append(f"включающий {known}")
        if distinctive:
            parts.append(f"отличающийся тем, что {distinctive}")
        effect_clean = (effect or '').strip()
        if effect_clean:
            effect_clean = re.sub(r'^\s*(обеспечивает|provides)\s+', '', effect_clean, flags=re.IGNORECASE).rstrip('.')
            if effect_clean:
                parts.append(f"обеспечивает {effect_clean}")
    formula = ', '.join([p.strip() for p in parts if p.strip()]).strip()
    if formula and not formula.endswith('.'):
        formula += '.'
    return formula

def generate_formula(idea: str, language: str = "ru") -> str:
    data = parse_input(idea, language=language)
    known_parts = _split_features(data.get("known", ""))
    distinctive_parts = _split_features(data.get("distinctive", ""))
    effect = (data.get("effect") or "").strip()
    known_str = ", ".join(known_parts)
    distinctive_str = ", ".join(distinctive_parts)
    return build_formula(data.get("name", ""), known_str, distinctive_str, effect, language=data.get("lang", language))

