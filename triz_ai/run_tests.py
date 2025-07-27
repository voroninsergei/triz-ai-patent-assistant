"""Utility script to run unit tests for coverage measurement.

This script imports the project modules and executes the unit tests defined
in the ``tests`` package.  It is used in conjunction with the Python
``trace`` module to collect line coverage metrics without requiring an
external dependency such as ``coverage.py``.  To use it, run:

    python -m trace --count --summary run_tests.py

The summary printed by ``trace`` will show the proportion of executed
statements per file.  A coverage of 90 % or higher indicates that the
tests exercise the majority of the codebase.
"""
import sys

# Ensure the source directory is on the path
sys.path.append('.')

def run_all_tests() -> None:
    """Import and run all test functions from the ``tests`` package."""
    import tests.test_generate_formula as tgf  # type: ignore
    import tests.test_prompt_enhancer as tpe  # type: ignore

    # Execute generate_formula tests
    tgf.test_generate_formula_short()
    tgf.test_generate_formula_long()
    tgf.test_generate_formula_medium_no_effect()
    # Execute prompt_enhancer tests
    tpe.test_enhance_formula_basic()
    tpe.test_enhance_formula_no_distinctive()

if __name__ == '__main__':
    run_all_tests()