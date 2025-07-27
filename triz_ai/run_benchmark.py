"""Benchmark script for evaluating generate_formula performance.

This script measures the response time and duplicate removal rate of the
`generate_formula` pipeline over a collection of invention descriptions.
It prints a tabular report to the console and appends the aggregated
results to ``leaderboard.md`` in the same directory.

Usage:

    python run_benchmark.py --data data/sample_ru.txt [--language ru]

If no ``--data`` file is provided, a built‑in set of sample descriptions
will be used.  To contribute new datasets, place a text file under
``benchmarks/data/`` and pass its path to the ``--data`` option.  Each
line in the file should contain a complete invention description.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import time
from typing import List, Dict

import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))  # add project root

from generate_formula import generate_formula, parse_input, deduplicate_features


def load_descriptions(path: pathlib.Path) -> List[str]:
    """Load descriptions from a text file, one per line."""
    descriptions: List[str] = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                descriptions.append(line)
    return descriptions


def run_benchmark(descriptions: List[str], language: str = 'ru') -> List[Dict[str, float]]:
    """Run the benchmark and return results.

    Parameters
    ----------
    descriptions : list of str
        List of invention descriptions.
    language : str
        Language code for lemmatisation.

    Returns
    -------
    list of dict
        Each dict contains ``id`` (1‑based), ``time_ms``, ``dup_rate`` and
        ``formula`` for a single description.
    """
    results: List[Dict[str, float]] = []
    for idx, text in enumerate(descriptions, start=1):
        # Measure time
        start = time.perf_counter()
        formula = generate_formula(text, style='compact', variants=1, language=language)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        # Compute duplicate rate using helper functions
        parts = parse_input(text, language=language)
        _, _, dup_rate = deduplicate_features(parts['known'], parts['distinctive'], language=language)
        results.append({
            'id': idx,
            'time_ms': round(elapsed_ms, 2),
            'dup_rate': round(dup_rate, 1),
            'formula': formula,
        })
    return results


def print_report(results: List[Dict[str, float]]) -> None:
    """Print results in a human‑readable table and aggregate statistics."""
    print(f"{'ID':<4}{'Time (ms)':<12}{'Dup rate (%)':<14}Formula")
    print('-' * 80)
    total_time = 0.0
    total_dup = 0.0
    for r in results:
        total_time += r['time_ms']
        total_dup += r['dup_rate']
        print(f"{r['id']:<4}{r['time_ms']:<12}{r['dup_rate']:<14}{r['formula']}")
    avg_time = total_time / len(results) if results else 0.0
    avg_dup = total_dup / len(results) if results else 0.0
    print('-' * 80)
    print(f"Average time: {avg_time:.2f} ms    Average dup_rate: {avg_dup:.1f}%")


def update_leaderboard(results: List[Dict[str, float]], language: str, dataset_name: str, author: str = 'anonymous') -> None:
    """Append aggregated results to the leaderboard file.

    The leaderboard file is a Markdown table stored at ``leaderboard.md``.
    If the file does not exist, it will be created with a header row.
    Each entry includes the dataset name, author, language, average time
    (ms), average dup_rate (%) and the date of submission.
    """
    from datetime import datetime

    lb_path = pathlib.Path(__file__).with_name('leaderboard.md')
    avg_time = sum(r['time_ms'] for r in results) / len(results) if results else 0.0
    avg_dup = sum(r['dup_rate'] for r in results) / len(results) if results else 0.0
    now = datetime.utcnow().strftime('%Y-%m-%d')
    row = [dataset_name, author, language, f"{avg_time:.2f}", f"{avg_dup:.1f}", now]
    # Ensure file exists and has header
    if not lb_path.exists():
        with lb_path.open('w', encoding='utf-8') as f:
            f.write('| Dataset | Author | Lang | Avg time (ms) | Avg dup_rate (%) | Date |\n')
            f.write('|-------|-------|------|--------------|-----------------|------|\n')
    with lb_path.open('a', encoding='utf-8') as f:
        f.write('|' + '|'.join(row) + '|\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Run benchmark for generate_formula.')
    parser.add_argument('--data', type=str, help='Path to a .txt file with one description per line')
    parser.add_argument('--language', choices=['ru', 'en'], default='ru', help='Language for lemmatisation')
    parser.add_argument('--author', type=str, default='anonymous', help='Your name or handle for the leaderboard')
    args = parser.parse_args()
    # Load descriptions
    if args.data:
        path = pathlib.Path(args.data)
        descriptions = load_descriptions(path)
        dataset_name = path.name
    else:
        # Fallback built‑in examples
        descriptions = [
            "Название: Система охлаждения двигателя. Известные признаки: содержит насос, радиатор и вентилятор. Отличительные признаки: имеет датчик температуры, управляющий скоростью вентилятора. Эффект: обеспечивает стабильную температуру без перегрева.",
            "Название: Насосная установка. Известные признаки: насос, насос, радиатор. Отличительные признаки: насос, датчик давления. Эффект: обеспечивает контроль давления.",
            "Название: Композитный материал. Известные признаки: матрица, армирующие волокна. Отличительные признаки: добавление наночастиц. Эффект: повышает прочность.",
        ]
        dataset_name = 'built_in'
    results = run_benchmark(descriptions, language=args.language)
    print_report(results)
    update_leaderboard(results, args.language, dataset_name, args.author)


if __name__ == '__main__':
    main()