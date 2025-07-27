"""
Command‑line interface for the TRIZ analysis system.

Usage:

    python cli.py --text "Описание изобретения..." [--max-keywords N] [--export output.docx]

    python cli.py --input-file description.txt --export report.docx

The script reads the invention description from the ``--text`` argument or
from a file supplied with ``--input-file``, runs the analysis using the
functions defined in ``triz_system.py``, prints the results to stdout and
optionally exports a Word document (.docx) with a table summarising the
keywords, IPC codes, TRIZ functions and contradictions.

This CLI illustrates the integration aspect mentioned in the improvement
proposal: users can run a single command ``analyze-invention`` (here
represented by executing this script) to obtain all analytical artefacts and
generate a report.
"""

import argparse
import sys
from typing import Optional

from triz_system import analyze_invention, export_report
from generate_formula import generate_formula
from prompt_enhancer import enhance_formula, export_enhancement_report

# Import additional modules for v3 functionality
from ipc_classifier import classify_ipc as classify_ipc_wrapper
from ariz import run_ariz_flow
from claim_validator import validate_claims
from drawing_mapper import generate_html_report
from security_utils import encrypt_and_sign


# Translation strings for CLI output.  The top‑level keys correspond to
# supported languages ('ru' for Russian, 'en' for English).  When adding
# new messages, ensure both languages are covered.
MESSAGES = {
    'ru': {
        'generated_formulas': 'Сгенерированные формулы:',
        'variant': 'Вариант',
        'generated_formula': 'Сгенерированная формула:',
        'improved_title': 'Улучшенное название:',
        'suggestions': 'Подсказки по неочевидности:',
        'justification': 'Обоснование патентоспособности:',
        'improved_report_saved': 'Улучшенный отчёт сохранён в файл {path}',
        'keywords': 'Ключевые слова:',
        'ipc_codes': 'Коды IPC:',
        'triz_functions': 'TRIZ‑функции:',
        'contradictions': 'Противоречия:',
        'contradiction_entry': '  - {type}: {desc}',
        'report_saved': 'Отчёт сохранён в файл {path}',
        'error_reading': 'Ошибка чтения файла {path}: {error}',
        'error_export': 'Ошибка при экспорте отчёта: {error}',
    },
    'en': {
        'generated_formulas': 'Generated formulas:',
        'variant': 'Variant',
        'generated_formula': 'Generated formula:',
        'improved_title': 'Improved title:',
        'suggestions': 'Non‑obviousness tips:',
        'justification': 'Patentability justification:',
        'improved_report_saved': 'Improved report saved to {path}',
        'keywords': 'Keywords:',
        'ipc_codes': 'IPC codes:',
        'triz_functions': 'TRIZ functions:',
        'contradictions': 'Contradictions:',
        'contradiction_entry': '  - {type}: {desc}',
        'report_saved': 'Report saved to file {path}',
        'error_reading': 'Error reading file {path}: {error}',
        'error_export': 'Error exporting report: {error}',
    },
}


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze an invention description using TRIZ system.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="Invention description text or claims")
    group.add_argument("--input-file", type=str, help="Path to a file containing the description or claims")
    parser.add_argument("--max-keywords", type=int, default=10, help="Maximum number of keywords to extract")
    parser.add_argument("--export", type=str, help="Path to .docx file for exporting report")
    parser.add_argument("--enhance", action="store_true", help="Generate and enhance patent formula instead of TRIZ analysis")
    # New flags for version 3 functionality
    parser.add_argument("--classify-ipc", action="store_true", help="Classify IPC codes based on extracted keywords and show top suggestions")
    parser.add_argument("--ariz", action="store_true", help="Run the simplified ARIZ 9-step algorithm and output the result")
    parser.add_argument("--validate", action="store_true", help="Validate the provided patent claims and report issues")
    parser.add_argument("--drawing-mapping-file", type=str, help="Path to JSON mapping of feature phrases to drawing positions for report generation")
    parser.add_argument("--secure-export", action="store_true", help="Encrypt exported .docx and sign it using password")
    parser.add_argument("--password", type=str, help="Password for encryption/signing when using --secure-export")
    # Additional options for formula generation
    parser.add_argument(
        "--style",
        choices=["compact", "verbose"],
        default="compact",
        help="Output style for generated formula: 'compact' removes duplicates, 'verbose' preserves them",
    )
    parser.add_argument(
        "--variants",
        type=int,
        default=1,
        help="Number of formula variants to generate (>=2 produces wide and narrow versions)",
    )
    parser.add_argument(
        "--language",
        choices=["ru", "en"],
        default="ru",
        help="Language of the description (affects lemmatisation for duplicate removal) and localisation",
    )
    args = parser.parse_args(argv)

    # Determine language for localisation
    lang = args.language if hasattr(args, 'language') else 'ru'
    msgs = MESSAGES.get(lang, MESSAGES['ru'])
    # Read text
    if args.text:
        text = args.text
    else:
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            # Localised error message
            print(msgs['error_reading'].format(path=args.input_file, error=e), file=sys.stderr)
            return 1

    # Handle version 3 specific actions first
    # IPC classification
    if args.classify_ipc:
        # Extract keywords and classify IPC
        keywords = analyze_invention(text, max_keywords=args.max_keywords)["keywords"]
        codes = classify_ipc_wrapper(keywords)
        print(msgs['ipc_codes'])
        for code in codes:
            print(f"  - {code}")
        # If also exporting, write simple report to file
        if args.export:
            try:
                with open(args.export, 'w', encoding='utf-8') as f:
                    f.write("\n".join(codes))
                print("\n" + msgs['report_saved'].format(path=args.export))
            except Exception as e:
                print(msgs['error_export'].format(error=e), file=sys.stderr)
                return 1
        return 0

    # ARIZ flow
    if args.ariz:
        result = run_ariz_flow(text)
        # Print step responses
        print("ARIZ steps and responses:")
        for item in result['steps']:
            print(f"{item['step']}: {item['response']}")
        print("\nPhysical conflict:")
        print(result['physical_conflict'])
        print("\nInventive principles:")
        for p in result['inventive_principles']:
            print(f"  - {p}")
        return 0

    # Claim validation
    if args.validate:
        valid, errs = validate_claims(text)
        if valid:
            print("Claims are valid.")
        else:
            print("Validation errors:")
            for err in errs:
                print(f"  - {err}")
        return 0

    # Drawing mapper
    if args.drawing_mapping_file:
        import json
        # Use the first line of text as the independent claim for mapping
        claim_line = text.strip().splitlines()[0] if text.strip() else ''
        try:
            with open(args.drawing_mapping_file, 'r', encoding='utf-8') as jf:
                mapping = json.load(jf)
        except Exception as e:
            print(msgs['error_reading'].format(path=args.drawing_mapping_file, error=e), file=sys.stderr)
            return 1
        html_report = generate_html_report(claim_line, mapping)
        # Write to export file or stdout
        if args.export:
            try:
                with open(args.export, 'w', encoding='utf-8') as f:
                    f.write(html_report)
                print("\n" + msgs['report_saved'].format(path=args.export))
            except Exception as e:
                print(msgs['error_export'].format(error=e), file=sys.stderr)
                return 1
        else:
            print(html_report)
        return 0

    # Enhancement (existing behaviour)
    if args.enhance:
        # Generate formula(s) using the specified style, variants and language
        formulas = generate_formula(text, style=args.style, variants=args.variants, language=args.language)
        # formulas may be a single string or a list of strings
        if isinstance(formulas, list):
            # Print all variants
            print(msgs['generated_formulas'])
            for idx, form in enumerate(formulas, start=1):
                print(f"\n{msgs['variant']} {idx}:")
                print(form)
            # Choose the first variant for enhancement
            formula_for_enhancement = formulas[0] if formulas else ""
        else:
            print(msgs['generated_formula'])
            print(formulas)
            formula_for_enhancement = formulas
        # Enhance the selected formula
        enhancements = enhance_formula(formula_for_enhancement)
        print(f"\n{msgs['improved_title']}")
        print(enhancements["title"])
        print(f"\n{msgs['suggestions']}")
        print(enhancements["non_obvious_suggestions"])
        print(f"\n{msgs['justification']}")
        print(enhancements["justification"])
        if args.export:
            try:
                export_enhancement_report(enhancements, args.export)
                # If secure export requested, encrypt the file as well
                if args.secure_export:
                    if not args.password:
                        print("Password is required for secure export", file=sys.stderr)
                        return 1
                    try:
                        # Read the exported report bytes
                        with open(args.export, 'rb') as rf:
                            report_bytes = rf.read()
                        encrypted, sig = encrypt_and_sign(report_bytes, args.password)
                        enc_path = args.export + '.enc'
                        sig_path = args.export + '.sig'
                        with open(enc_path, 'wb') as ef:
                            ef.write(encrypted)
                        with open(sig_path, 'wb') as sf:
                            sf.write(sig)
                        print("\nEncrypted report saved to " + enc_path)
                        print("Signature saved to " + sig_path)
                    except Exception as e:
                        print(msgs['error_export'].format(error=e), file=sys.stderr)
                        return 1
                else:
                    print("\n" + msgs['improved_report_saved'].format(path=args.export))
            except Exception as e:
                # Localised error message
                print(msgs['error_export'].format(error=e), file=sys.stderr)
                return 1
    else:
        # Analyze TRIZ
        analysis = analyze_invention(text, max_keywords=args.max_keywords)
        # Localised section headings
        print(msgs['keywords'])
        for kw in analysis["keywords"]:
            print(f"  - {kw}")
        print("\n" + msgs['ipc_codes'])
        for code in analysis["ipc_codes"]:
            print(f"  - {code}")
        print("\n" + msgs['triz_functions'])
        for func in analysis["triz_functions"]:
            print(f"  - {func}")
        print("\n" + msgs['contradictions'])
        for c in analysis["contradictions"]:
            # Localise the contradiction type only for English; Russian capitalisation is handled via capitalize()
            c_type = c['type'].capitalize() if lang == 'ru' else c['type'].capitalize()
            print(msgs['contradiction_entry'].format(type=c_type, desc=c['description']))
        if args.export:
            try:
                export_report(analysis, args.export)
                # If secure export requested, encrypt the docx file
                if args.secure_export:
                    if not args.password:
                        print("Password is required for secure export", file=sys.stderr)
                        return 1
                    try:
                        with open(args.export, 'rb') as rf:
                            report_bytes = rf.read()
                        encrypted, sig = encrypt_and_sign(report_bytes, args.password)
                        enc_path = args.export + '.enc'
                        sig_path = args.export + '.sig'
                        with open(enc_path, 'wb') as ef:
                            ef.write(encrypted)
                        with open(sig_path, 'wb') as sf:
                            sf.write(sig)
                        print("\nEncrypted report saved to " + enc_path)
                        print("Signature saved to " + sig_path)
                    except Exception as e:
                        print(msgs['error_export'].format(error=e), file=sys.stderr)
                        return 1
                else:
                    print("\n" + msgs['report_saved'].format(path=args.export))
            except Exception as e:
                print(msgs['error_export'].format(error=e), file=sys.stderr)
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())