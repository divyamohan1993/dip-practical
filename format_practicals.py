"""Apply uniform Aim / Theory / Code / Output / Analysis formatting with
color-coded sections and uniform code styling to every Practical_N.ipynb.

The format follows practical-format.md:
    1. Aim
    2. Theory
    3. Code
    4. Output
    5. Analysis

Color coding (consistent across all practicals):
    Aim       — navy blue
    Theory    — purple
    Code      — green (matches code blocks)
    Output    — amber/orange
    Analysis  — maroon/red

Page setup: 1-inch margins all sides, justified text, Times New Roman 12pt.
Code blocks: JetBrains Mono / Source Code Pro 10pt with green left border.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent

# CSS preamble injected as the first markdown cell after the Colab badge.
# Lives inside a <style> tag so it applies whenever the notebook is rendered
# (Jupyter, nbconvert HTML, nbconvert PDF via WeasyPrint or LaTeX).
PREAMBLE_CSS = """<style>
/* =====================================================================
   Practical Handbook — Uniform Print Formatting (CSU2543 Digital Image Processing)
   Sections are color-coded: Aim (blue), Theory (purple), Code (green),
   Output (amber), Analysis (maroon). Code blocks are uniform across all
   practicals. Page layout: 1-inch margins, justified text, Times New Roman.
   ===================================================================== */
@page { margin: 1in; }
@media print {
  body, .jp-Notebook, .jupyter-renderer { background: white !important; }
  .jp-CodeMirrorEditor, .CodeMirror { font-size: 10pt !important; }
  .jp-Cell-inputCollapser, .jp-Cell-outputCollapser, .jp-Toolbar { display: none !important; }
  .dip-section-marker { page-break-inside: avoid; }
}

.jp-RenderedHTMLCommon, .jp-RenderedMarkdown {
  font-family: 'Times New Roman', Georgia, serif;
  font-size: 12pt;
  line-height: 1.55;
  text-align: justify;
}

/* Section markers — colored heading bars */
.dip-section-marker {
  display: block;
  font-weight: bold;
  font-size: 1.35em;
  padding: 0.45em 0.7em;
  margin: 1.1em 0 0.6em 0;
  border-left: 6px solid;
  border-radius: 3px;
  letter-spacing: 0.02em;
  page-break-after: avoid;
}
.dip-section-aim      { color: #003c8f; background: #e3f2fd; border-color: #1565c0; }
.dip-section-theory   { color: #4a148c; background: #f3e5f5; border-color: #6a1b9a; }
.dip-section-code     { color: #1b5e20; background: #e8f5e9; border-color: #2e7d32; }
.dip-section-output   { color: #e65100; background: #fff3e0; border-color: #ef6c00; }
.dip-section-analysis { color: #b71c1c; background: #ffebee; border-color: #c62828; }

/* Sub-section headings within a section ("Part 1", "Part 2", ...) */
.dip-subsection {
  font-weight: 600;
  font-size: 1.1em;
  margin: 0.9em 0 0.4em 0;
  color: #2e7d32;
  border-bottom: 1px solid #c8e6c9;
  padding-bottom: 0.15em;
  page-break-after: avoid;
}

/* Code cells — uniform JetBrains Mono / Source Code Pro across all practicals */
.jp-CodeMirrorEditor, .jp-CodeCell .jp-InputArea-editor,
.CodeMirror, pre, .highlight, code {
  font-family: 'JetBrains Mono', 'Source Code Pro', Consolas, 'Courier New', monospace !important;
}
.jp-CodeCell .jp-InputArea-editor, .CodeMirror, pre {
  font-size: 10pt !important;
  background: #f6f8fa !important;
  border-left: 3px solid #2e7d32 !important;
  border-radius: 0 !important;
  padding: 8px 12px !important;
}
code { background: #f6f8fa; padding: 1px 5px; border-radius: 2px; font-size: 0.95em; }

/* Output cells — amber tint, matching the Output section colour */
.jp-OutputArea-output {
  border-left: 3px solid #ef6c00 !important;
  background: #fffaf3 !important;
  padding: 6px 10px !important;
}

/* Analysis question lists */
.dip-analysis-list { padding-left: 1.4em; }
.dip-analysis-list li { margin-bottom: 0.5em; text-align: justify; }
</style>"""


def md_cell(source):
    return {"cell_type": "markdown", "metadata": {}, "source": [source] if isinstance(source, str) else source}


def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [source] if isinstance(source, str) else source,
    }


def section_html(name, key):
    """Render a section marker as an HTML span that gets the colored bar style."""
    return f'<span class="dip-section-marker dip-section-{key}">{name}</span>'


def cell_text(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def is_markdown(cell):
    return cell.get("cell_type") == "markdown"


def is_code(cell):
    return cell.get("cell_type") == "code"


def has_colab_badge(cell):
    return is_markdown(cell) and "colab-badge" in cell_text(cell).lower() and "open in colab" in cell_text(cell).lower()


def is_title_heading(cell):
    if not is_markdown(cell):
        return False
    return bool(re.match(r"\s*#\s+Practical\s+\d", cell_text(cell)))


SECTION_PATTERNS = {
    "aim": [r"^\s*##\s*Aim\b", r"^\s*##\s*Objective\b", r"\*\*Objective:\*\*", r"\*\*Aim:\*\*"],
    "theory": [r"^\s*##\s*Theory\b", r"^\s*##\s*Algorithm\b", r"\*\*Algorithm:\*\*", r"\*\*Formula:\*\*",
               r"\*\*Problem Statement\b", r"\*\*Theory:\*\*"],
    "code": [r"^\s*##\s*Code\b", r"^\s*##\s*Setup\b", r"^\s*##\s*Part\s+\d", r"^\s*##\s*Bonus\b",
             r"^\s*###\s*Part\s+\d", r"^\s*###\s*Setup\b"],
    "output": [r"^\s*##\s*Output\b"],
    "analysis": [r"^\s*##\s*Analysis\b", r"^\s*##\s*Analysis\s+Questions\b"],
}


def classify_cell(cell):
    """Return ('aim'|'theory'|'code'|'output'|'analysis'|None, is_subsection)."""
    if not is_markdown(cell):
        return None, False
    text = cell_text(cell)
    for section, patterns in SECTION_PATTERNS.items():
        for p in patterns:
            if re.search(p, text, flags=re.IGNORECASE | re.MULTILINE):
                # subsection if it's a "Part N" or starts with ###
                is_sub = bool(re.search(r"Part\s+\d|Bonus|Setup", text, flags=re.IGNORECASE)) and section == "code"
                return section, is_sub
    return None, False


# Practical-specific Aim and Theory text. For P1-P6 we extract a concise Aim
# from the existing objective text; Theory is built from existing algorithm /
# formula content where present.

PRACTICAL_META = {
    1: {
        "title": "Loading and Displaying Digital Images",
        "aim": ("To learn how to load, display, and inspect digital images using OpenCV "
                "and Matplotlib, and to characterise their basic properties "
                "(shape, intensity range, mean, standard deviation) and pixel-intensity "
                "distribution via the histogram."),
        "theory": (
            "A digital image is the discrete sampled representation of a continuous "
            "two-dimensional intensity function $f(x,y)$ on a regular spatial grid. "
            "After sampling on an $M\\times N$ grid and quantising the amplitude to $L$ "
            "intensity levels, the image is stored as an $M\\times N$ matrix of unsigned "
            "integers. For an 8-bit grayscale image $L=256$, so each pixel lies in $[0,255]$ "
            "with $0$ encoding pure black and $255$ encoding pure white.\n\n"
            "**Histogram.** The histogram $h(r_k)$ counts the number of pixels with "
            "intensity $r_k$ for $k=0,1,\\dots,L-1$. The shape of the histogram captures "
            "the global tonal characteristics of the image: a narrow cluster indicates "
            "low contrast, a wide spread indicates high contrast, and bimodality often "
            "signals a foreground/background separation."
        ),
    },
    2: {
        "title": "Impact of Sampling Rate on Spatial Resolution",
        "aim": ("To evaluate the relationship between the sampling rate $N$ and the "
                "spatial resolution of digital images by progressively halving the pixel "
                "count of an image and analysing the resulting loss of geometric detail "
                "and the emergence of aliasing artefacts."),
        "theory": (
            "Spatial resolution is the size of the smallest perceptible detail in an image, "
            "and is determined by the sampling rate applied during digitisation. The "
            "Nyquist–Shannon sampling theorem states that to reconstruct a band-limited "
            "signal without aliasing, the sampling rate must be at least twice the highest "
            "spatial frequency present.\n\n"
            "Progressive downsampling by factors of two ($1024 \\to 512 \\to 256 \\to \\dots$) "
            "halves the sampling rate at each step. Below the Nyquist limit, high-frequency "
            "structure folds back into low frequencies as **aliasing**, visible as jagged "
            "lines and stair-stepping along oblique edges. Upscaling a downsampled image back "
            "to the original size cannot recover the lost information; the result is "
            "characteristically blocky."
        ),
    },
    3: {
        "title": "Image Negation, Subtraction, and Inversion",
        "aim": ("To implement and analyze fundamental intensity-transformation operations: "
                "image negation, image-pair subtraction, and intensity inversion, and to "
                "demonstrate their use in medical imaging applications such as digital "
                "subtraction angiography and shading correction."),
        "theory": (
            "**Negation.** The image negative reverses the intensity scale via $s = (L-1) - r$ "
            "where $L$ is the number of intensity levels. It enhances visibility of detail in "
            "predominantly dark regions (e.g., bright lesions on a dark X-ray).\n\n"
            "**Image subtraction.** The absolute difference $g(x,y) = \\lvert f_1(x,y) - f_2(x,y) \\rvert$ "
            "isolates structures that have changed between two frames. In **digital subtraction "
            "angiography** (DSA) a contrast-enhanced live image is subtracted from a baseline mask "
            "to reveal blood vessels; in **shading correction** a sensor-bias image is subtracted "
            "from the raw acquisition.\n\n"
            "**Inversion** is identical to negation when applied to the difference image; it is "
            "useful when the difference is sparse and a dark-on-light rendering is preferred."
        ),
    },
    4: {
        "title": "Gamma Correction and Power-Law Transformations",
        "aim": ("To implement and analyze the power-law (gamma) intensity transformation and the "
                "logarithmic transformation, and to use them for contrast enhancement of dark, "
                "bright, and low-contrast images."),
        "theory": (
            "The **power-law transformation** is\n\n"
            "$$ s = c \\cdot r^{\\gamma} $$\n\n"
            "with $r,s \\in [0,1]$. With $c=1$ the curve passes through $(0,0)$ and $(1,1)$ for any $\\gamma>0$. "
            "$\\gamma<1$ expands dark intensities and compresses bright ones (brightening); "
            "$\\gamma>1$ does the opposite (darkening). $\\gamma=1, c=1$ is the identity transform.\n\n"
            "Display devices have an inherent gamma (typically $\\gamma_{display}\\approx 2.2$); to "
            "compensate, images are pre-corrected with $\\gamma_{pre}=1/\\gamma_{display}\\approx 0.45$ "
            "before being sent to the display.\n\n"
            "The **log transformation** $s = c \\cdot \\log(1+r)$ compresses dynamic range and is "
            "the standard choice for displaying Fourier-spectrum magnitude images."
        ),
    },
    5: {
        "title": "Histogram Equalization",
        "aim": ("To understand and implement histogram equalization, a global contrast-enhancement "
                "technique that redistributes pixel intensities so the output histogram approximates "
                "a uniform distribution."),
        "theory": (
            "For a discrete image with $L$ intensity levels, the probability density (PDF), "
            "cumulative distribution (CDF), and the equalization transfer function are\n\n"
            "$$ p(r_k) = \\frac{n_k}{n}, \\qquad T(r_k) = \\sum_{j=0}^{k} p(r_j), \\qquad s_k = \\lfloor (L-1)\\,T(r_k) + 0.5 \\rfloor $$\n\n"
            "Mapping every input intensity $r$ through $T$ stretches the histogram across the full "
            "$[0,L-1]$ range. Because intensities are discrete, the equalised histogram is only "
            "approximately uniform—pixels that were originally identical remain identical after "
            "the mapping, so true uniformity is unreachable."
        ),
    },
    6: {
        "title": "Histogram Matching and Specification",
        "aim": ("To understand and implement histogram matching (specification) — a generalisation of "
                "histogram equalization that transforms a source image so its histogram approximates "
                "a desired target distribution rather than a uniform one."),
        "theory": (
            "Given the source CDF $T(r) = \\mathrm{CDF}_s(r)$ and the target CDF $G(z) = \\mathrm{CDF}_t(z)$, "
            "the matched intensity for each source value $r$ is obtained by inverting the target CDF at $T(r)$:\n\n"
            "$$ z = G^{-1}\\!\\bigl(T(r)\\bigr) $$\n\n"
            "Operationally, a 256-entry lookup table is built by, for each $r$, finding the $z$ that "
            "minimises $\\lvert G(z) - T(r) \\rvert$; the source image is then remapped through this table. "
            "Histogram **equalization** is the special case in which $G$ is the linear ramp $z/(L-1)$."
        ),
    },
    7: {
        "title": "2D Correlation and Convolution",
        "aim": ("To implement and analyze the two fundamental linear spatial operations of digital "
                "image processing — correlation and convolution — from first principles, demonstrate "
                "the impulse-response interpretation that distinguishes them, and apply standard "
                "kernels (averaging, Laplacian, Sobel) to a real image."),
        "theory": (
            "Let $f$ be an $M\\times N$ image and $w$ an $m\\times n$ kernel with $m=2a+1, n=2b+1$.\n\n"
            "$$ (w \\star f)(x,y) = \\sum_{s=-a}^{a}\\sum_{t=-b}^{b} w(s,t)\\,f(x+s,y+t) \\qquad\\text{correlation} $$\n\n"
            "$$ (w * f)(x,y) = \\sum_{s=-a}^{a}\\sum_{t=-b}^{b} w(s,t)\\,f(x-s,y-t) \\qquad\\text{convolution} $$\n\n"
            "**Identity:** $w * f \\;=\\; \\mathrm{rot}_{180}(w) \\star f$. Consequently a unit-impulse input "
            "writes $\\mathrm{rot}_{180}(w)$ into the correlation output and $w$ itself into the convolution "
            "output—this is the operational definition. The two operations coincide whenever $w$ is "
            "symmetric under 180° rotation (box, Gaussian, standard Laplacian); they differ for "
            "asymmetric kernels (Sobel, Prewitt, motion blur)."
        ),
    },
    8: {
        "title": "Spatial Filtering — Smoothing and Sharpening",
        "aim": ("To implement and analyze the four canonical spatial-domain filters of digital image "
                "processing: the box (averaging) filter and median filter for noise smoothing, and "
                "the Laplacian and Sobel operators for sharpening and edge detection."),
        "theory": (
            "**Box (mean) filter — linear, smoothing:** $\\hat f(x,y) = \\frac{1}{mn}\\sum_{(s,t)\\in S_{xy}} f(s,t)$.\n\n"
            "**Median filter — non-linear, order-statistic:** $\\hat f(x,y) = \\mathrm{median}\\{f(s,t):(s,t)\\in S_{xy}\\}$. "
            "Because the median is robust to extreme outliers, it removes salt-and-pepper noise "
            "without blurring step edges.\n\n"
            "**Laplacian — second derivative, sharpening:**\n\n"
            "$$ \\nabla^{2}f \\approx f(x{+}1,y) + f(x{-}1,y) + f(x,y{+}1) + f(x,y{-}1) - 4 f(x,y); \\qquad g = f - \\nabla^{2}f. $$\n\n"
            "**Sobel — first derivative, edge detection:** orthogonal kernels $G_x, G_y$ produce "
            "the gradient magnitude $|G|\\approx |G_x|+|G_y|$ and direction $\\theta=\\arctan(G_y/G_x)$."
        ),
    },
}


def build_practical(num):
    meta = PRACTICAL_META[num]
    src = ROOT / f"Practical_{num}.ipynb"
    with open(src) as f:
        nb = json.load(f)

    cells = nb["cells"]

    # 1. Locate Colab badge cell (cell 0 typically); the existing title cell
    # is found by iterating below rather than precomputed.
    badge_idx = next((i for i, c in enumerate(cells) if has_colab_badge(c)), -1)

    # If the existing notebook already has an "Aim" or "Theory" markdown cell as
    # second cell, we'll prepend our preamble + replace those headings;
    # otherwise we build a fresh top-of-notebook structure.

    new_cells = []

    # Keep Colab badge if present
    if badge_idx == 0 and badge_idx >= 0:
        new_cells.append(cells[0])
        cells_after_badge = cells[1:]
    else:
        cells_after_badge = cells

    # Insert preamble (CSS) cell
    new_cells.append(md_cell(PREAMBLE_CSS))

    # Insert / preserve title heading
    title_text = f"# Practical {num}: {meta['title']}"
    new_cells.append(md_cell(title_text))

    # Insert Aim section
    new_cells.append(md_cell(
        f"{section_html('1. Aim', 'aim')}\n\n{meta['aim']}"
    ))

    # Insert Theory section
    new_cells.append(md_cell(
        f"{section_html('2. Theory', 'theory')}\n\n{meta['theory']}"
    ))

    # Insert Code section header
    new_cells.append(md_cell(section_html("3. Code", "code")))

    # Now copy through the original code + sub-section cells, skipping
    # superseded items (old objectives, old analysis, the original title).
    for i, cell in enumerate(cells_after_badge):
        if cell is new_cells[0]:
            continue
        if is_title_heading(cell):
            continue  # we already wrote the canonical title

        section, _ = classify_cell(cell)

        # Drop old objective/aim cells and old analysis cells; we'll re-inject ours.
        if section == "aim":
            continue
        if section == "analysis":
            continue
        if section == "theory":
            # Skip standalone old theory cells but keep formula hints if mixed with title text.
            txt = cell_text(cell)
            # If theory cell is *just* a heading or short objective+formula, drop;
            # otherwise convert to subsection.
            if re.match(r"^\s*##\s*(Theory|Algorithm)\b", txt, re.IGNORECASE):
                continue
            # else keep as-is (it'll appear under Code section, harmless)

        # Convert "## Part N: ..." or "## Bonus: ..." or "## Setup" to a sub-section span.
        if is_markdown(cell):
            txt = cell_text(cell)
            converted = re.sub(
                r"^\s*##\s+(Part\s+\d+[^\n]*|Bonus[^\n]*|Setup[^\n]*)",
                lambda m: f'<span class="dip-subsection">{m.group(1).strip()}</span>',
                txt,
                count=1,
                flags=re.MULTILINE,
            )
            cell = md_cell(converted)

        new_cells.append(cell)

    # Append explicit Output section marker at the end of code blocks.
    # Output is implicit (cell outputs render below code) — we add a marker
    # so the printed handbook clearly identifies "Output" before the analysis.
    new_cells.append(md_cell(
        f"{section_html('4. Output', 'output')}\n\n"
        "*All output (printed values, computed statistics, and rendered figures) "
        "appears immediately below the corresponding code cells when this notebook "
        "is executed top-to-bottom.*"
    ))

    # Append Analysis section. Look for the *original* analysis content in the
    # source notebook and re-attach it.
    analysis_blocks = []
    for cell in cells_after_badge:
        sec, _ = classify_cell(cell)
        if sec == "analysis" and is_markdown(cell):
            txt = cell_text(cell)
            # Strip leading "## Analysis Questions" heading
            txt = re.sub(r"^\s*##\s*Analysis\s*(?:Questions)?\s*\n+", "", txt, flags=re.IGNORECASE)
            analysis_blocks.append(txt.strip())

    analysis_body = "\n\n".join(analysis_blocks) if analysis_blocks else (
        "*Refer to the practical handbook for analysis questions and discussion.*"
    )
    new_cells.append(md_cell(
        f"{section_html('5. Analysis', 'analysis')}\n\n{analysis_body}"
    ))

    nb["cells"] = new_cells
    nb.setdefault("nbformat", 4)
    nb.setdefault("nbformat_minor", 4)
    nb.setdefault("metadata", {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12.0"},
    })

    with open(src, "w") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    return len(new_cells)


def main():
    for n in range(1, 9):
        c = build_practical(n)
        print(f"Practical_{n}.ipynb: {c} cells")


if __name__ == "__main__":
    main()
