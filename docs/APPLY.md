# English UI labels + formula connectors

## What this does
- Replaces Russian "Formula style" option labels with English:
  - "компактный (без повторений)" → "compact (no repetition)"
  - "подробный (с повторениями)" → "detailed (with repetition)"
- Ensures formulas use English connectors when Formula language is English:
  - "включающий" → "comprising"
  - "отличающийся тем, что" → "wherein"
  - "обеспечивает" → "provides"
- Adds robust language normalization, so values like "English" / "EN" / "en-US" are treated as `en`.

## How to apply
1) Copy the files from `replacements/` over your repo files (2 places):
   - Replace root `generate_formula.py`
   - Replace `triz_ai/generate_formula.py`
2) Update the UI labels by running from your repo root:
   ```bash
   python scripts/replace_ui_style_labels.py .
   ```
3) Test in the Streamlit UI with `Formula language = English` and check that the formula uses *comprising / wherein / provides*.
