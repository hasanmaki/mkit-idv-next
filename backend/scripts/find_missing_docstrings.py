"""Scan the package for missing docstrings and print a report.

Usage: python scripts/find_missing_docstrings.py
"""

import ast
import os
import sys
from typing import List, Tuple

ROOT = os.path.join(os.path.dirname(__file__), "..")
PACKAGE = os.path.join(ROOT, "app")

missing: List[Tuple[str, int, str]] = []
missing_module: List[str] = []

for dirpath, dirnames, filenames in os.walk(PACKAGE):
    for fname in filenames:
        if not fname.endswith(".py"):
            continue
        path = os.path.join(dirpath, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
            node = ast.parse(src, filename=path)
        except Exception as e:
            print(f"ERROR parsing {path}: {e}")
            continue

        # Module docstring
        mod_doc = ast.get_docstring(node)
        if not mod_doc:
            missing_module.append(path)

        for n in node.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(n)
                if not doc:
                    missing.append((path, n.lineno, f"function {n.name}"))
            elif isinstance(n, ast.ClassDef):
                cdoc = ast.get_docstring(n)
                if not cdoc:
                    missing.append((path, n.lineno, f"class {n.name}"))
                for m in n.body:
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        md = ast.get_docstring(m)
                        if not md:
                            missing.append((
                                path,
                                m.lineno,
                                f"method {n.name}.{m.name}",
                            ))

# Print report
print("\nDocstring scan report:\n")
if missing_module:
    print("Missing module docstrings (files):")
    for p in missing_module:
        print(f"  - {os.path.relpath(p, ROOT)}")
else:
    print("No missing module docstrings found.")

if missing:
    print("\nMissing docstrings (count: {}):".format(len(missing)))
    for p, lineno, what in missing:
        print(f"  - {os.path.relpath(p, ROOT)}:{lineno} -> {what}")
else:
    print("No missing function/class/method docstrings found.")

print("\nSummary:")
print(f"  files missing module docstrings: {len(missing_module)}")
print(f"  missing docs found: {len(missing)}")

sys.exit(0 if (not missing_module and not missing) else 2)
