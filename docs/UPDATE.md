    # English language support update (drop-in)

    This bundle contains:
    - `en_synonyms/` — new package (mirrors `ru_synonyms` API).
    - `replacements/generate_formula.py` — drop-in replacement for root file.
    - `replacements/triz_ai/generate_formula.py` — drop-in replacement for package.
    - `patches/ru_synonyms_get_synonyms_alias.patch` — adds `get_synonyms(...)` alias to `ru_synonyms`.
    - `patches/readme_en_example.patch` — adds an English quick-start snippet to README.

    ## Apply (option A): copy files
    1. Copy the entire `en_synonyms/` folder into the repository root (next to `ru_synonyms/`).
    2. Replace:
       - root-level `generate_formula.py` with `replacements/generate_formula.py`
       - `triz_ai/generate_formula.py` with `replacements/triz_ai/generate_formula.py`
    3. (Optional) Apply the README patch:
       ```bash
       git apply patches/readme_en_example.patch
       ```
    4. (Optional) Add alias method to `ru_synonyms` with patch (safe, no behavior changes):
       ```bash
       git apply patches/ru_synonyms_get_synonyms_alias.patch
       ```

    ## Apply (option B): patch-only
    If you prefer patches, adapt paths as needed and run `git apply` for both patch files.

    ## Hugging Face Space
    - Use the same files; copy `en_synonyms/` and replace `generate_formula.py` in both locations.
    - No hard dependency on `nltk`. If you want richer synonyms on Spaces, add `nltk>=3.8` to `requirements.txt`.
      The code will gracefully fall back to the small built-in graph if WordNet data is absent.

    ## Sanity check
    ```python
    from triz_ai.generate_formula import generate_formula

    idea_en = (
        "Title: Fuel delivery device
"
        "Known features: includes a pump and a filter
"
        "Distinctive features: further comprising a temperature sensor controlling fan speed
"
        "Effect: provides stable temperature without overheating"
    )
    print(generate_formula(idea_en, language='en'))
    # => Fuel delivery device, comprising a pump and a filter, wherein further comprising a temperature sensor controlling fan speed, provides stable temperature without overheating.
    ```
