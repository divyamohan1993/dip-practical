"""Add print-only colour-coded section banners to all 8 Flask practical templates.

The banners only render when printing (Ctrl+P). On screen the page looks
identical to before. When printed, the page lays out as:

    Aim       (blue)    — was 'Objective' / 'Aim'
    Theory    (purple)  — wraps theory-box / formula-box content
    Code      (green)   — covers all 'Part N' section cards
    Output    (orange)  — banner between code parts and analysis
    Analysis  (red)     — wraps Analysis Questions

Templates: app/templates/practicals/p01.html .. p08.html
"""
import re
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "app" / "templates" / "practicals"

AIM_BANNER = '<span class="print-only dip-section-marker dip-section-aim">1. Aim</span>'
THEORY_BANNER = '<span class="print-only dip-section-marker dip-section-theory">2. Theory</span>'
CODE_BANNER = '<span class="print-only dip-section-marker dip-section-code">3. Code</span>'
OUTPUT_BANNER = '<span class="print-only dip-section-marker dip-section-output">4. Output</span>'
ANALYSIS_BANNER = '<span class="print-only dip-section-marker dip-section-analysis">5. Analysis</span>'


def add_banners_to_template(path: Path) -> bool:
    text = path.read_text()
    if "dip-section-aim" in text:
        # Already processed; idempotent skip.
        return False

    original = text

    # 1. Insert Aim banner BEFORE the first section-card containing "Objective" or "Aim"
    pattern_aim = re.compile(
        r'(<div class="section-card">\s*\n\s*<h3>(?:Objective|Aim)</h3>)'
    )
    text = pattern_aim.sub(AIM_BANNER + "\n" + r"\1", text, count=1)

    # 2. Insert Theory banner just before the theory-box / formula-box
    pattern_theory = re.compile(
        r'(\s*)(<div class="theory-box">)'
    )
    # Only apply once: at the first match.
    m = pattern_theory.search(text)
    if m:
        idx = m.start()
        text = text[:idx] + m.group(1) + THEORY_BANNER + "\n" + m.group(1) + m.group(2) + text[m.end():]

    # 3. Insert Code banner before the first "Part N" section-card
    pattern_code = re.compile(
        r'(<div class="section-card">\s*\n\s*<h3>Part\s+\d)'
    )
    text = pattern_code.sub(CODE_BANNER + "\n" + r"\1", text, count=1)

    # 4. Insert Output + Analysis banners just before the analysis-box
    pattern_analysis = re.compile(
        r'(<div class="analysis-box">)'
    )
    text = pattern_analysis.sub(
        OUTPUT_BANNER + "\n\n" + ANALYSIS_BANNER + "\n" + r"\1",
        text, count=1
    )

    if text == original:
        return False
    path.write_text(text)
    return True


def main():
    for n in range(1, 9):
        path = TEMPLATE_DIR / f"p{n:02d}.html"
        if not path.exists():
            print(f"skip: {path.name} (missing)")
            continue
        changed = add_banners_to_template(path)
        print(f"{'updated' if changed else 'unchanged'}: {path.name}")


if __name__ == "__main__":
    main()
