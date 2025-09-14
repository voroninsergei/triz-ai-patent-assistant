#!/usr/bin/env python3
# Replace Russian Formula style labels with English across repo files
import os, sys

RU_COMPACT = "компактный (без повторений)"
RU_DETAILED = "подробный (с повторениями)"
EN_COMPACT = "compact (no repetition)"
EN_DETAILED = "detailed (with repetition)"

exts = {".py", ".pyw", ".pyi"}

root = sys.argv[1] if len(sys.argv) > 1 else "."
changed = 0
for dirpath, _, filenames in os.walk(root):
    for name in filenames:
        if os.path.splitext(name)[1].lower() in exts:
            p = os.path.join(dirpath, name)
            try:
                with open(p, "r", encoding="utf-8") as f:
                    txt = f.read()
            except Exception:
                continue
            if (RU_COMPACT in txt) or (RU_DETAILED in txt):
                txt2 = txt.replace(RU_COMPACT, EN_COMPACT).replace(RU_DETAILED, EN_DETAILED)
                if txt2 != txt:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(txt2)
                    print("Updated:", p)
                    changed += 1
print(f"Done. Files updated: {changed}")
