"""Inject literal Python code (from each Practical_N.ipynb) under the "Code"
banner of each Flask practical template, and add a print-only "Output"
container that the front-end JS will populate with cloned result images
right before printing.

Result for the printed practical handbook:
    1. Aim
    2. Theory
    3. Code     <-- literal Python source
    4. Output   <-- the rendered figures and computed values
    5. Analysis
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE_DIR = ROOT / "app" / "templates" / "practicals"


def extract_notebook_code(notebook_path: Path) -> str:
    """Concatenate every code cell from the notebook with separators."""
    with open(notebook_path) as f:
        nb = json.load(f)

    blocks = []
    for cell in nb["cells"]:
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        text = "".join(src) if isinstance(src, list) else src
        if text.strip():
            blocks.append(text.rstrip())

    return "\n\n# " + ("-" * 70) + "\n\n".join(["", *blocks])


def patch_template(num: int) -> bool:
    template = TEMPLATE_DIR / f"p{num:02d}.html"
    notebook = ROOT / f"Practical_{num}.ipynb"
    if not template.exists() or not notebook.exists():
        return False

    text = template.read_text()
    if 'class="print-only literal-code"' in text:
        # Idempotent — already patched.
        return False

    code = extract_notebook_code(notebook)
    code_html = (
        '<pre class="print-only literal-code"><code>'
        + escape(code)
        + '</code></pre>'
    )

    # Insert literal code block immediately after the Code banner.
    # Use a callable replacement so that backslashes in `code_html` (e.g. \u
    # escapes from the notebook source) are not reinterpreted by re.sub.
    code_marker = '<span class="print-only dip-section-marker dip-section-code">3. Code</span>'
    if code_marker in text:
        text2 = text.replace(code_marker, code_marker + "\n" + code_html, 1)
    else:
        text2 = text

    # Insert print-only Output container right after the Output banner.
    output_marker = '<span class="print-only dip-section-marker dip-section-output">4. Output</span>'
    output_div = '<div class="print-only output-collection" id="printOutput" aria-label="Result figures and computed outputs"></div>'
    if output_marker in text2:
        text3 = text2.replace(output_marker, output_marker + "\n" + output_div, 1)
    else:
        text3 = text2

    if text3 == text:
        return False
    template.write_text(text3)
    return True


def main():
    for n in range(1, 9):
        changed = patch_template(n)
        print(f"p{n:02d}.html: {'patched' if changed else 'already up-to-date'}")


if __name__ == "__main__":
    main()
