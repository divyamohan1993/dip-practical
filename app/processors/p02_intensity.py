"""
Practical 2 — Intensity Transformations (Gonzalez & Woods Ch. 3.2).

Provides image processing functions for log transforms, gamma (power-law)
corrections, contrast stretching, intensity negation, bit-plane slicing,
thresholding, and educational comparison utilities.

All transforms use NumPy arithmetic on grayscale uint8 arrays.
Matplotlib figures are built with figure-scoped methods for thread safety.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from app.processors.common import (
    load_image,
    image_to_base64_png,
    fig_to_base64,
    IMAGES_DIR,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _image_stats(img):
    """Return min / max / mean statistics for a uint8 image array."""
    return {
        "min": int(img.min()),
        "max": int(img.max()),
        "mean": round(float(img.mean()), 2),
    }


def _make_transform_plot(r, s, title, xlabel="Input Intensity (r)",
                         ylabel="Output Intensity (s)", label=None,
                         figsize=(5, 4)):
    """
    Plot a single intensity-transform curve *s = T(r)*.

    Parameters
    ----------
    r : array-like
        Input intensities (x-axis).
    s : array-like
        Output intensities (y-axis).
    title : str
        Axes title.
    xlabel, ylabel : str
        Axis labels.
    label : str or None
        Legend label for the curve.
    figsize : tuple
        Figure dimensions in inches.

    Returns
    -------
    str
        Base64-encoded PNG of the plot.
    """
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.plot(r, s, color='#2c3e50', linewidth=2, label=label)
    ax.plot([0, 255], [0, 255], 'k--', linewidth=0.8, alpha=0.4,
            label='Identity')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    if label:
        ax.legend(fontsize=9)
    fig.tight_layout()
    return fig_to_base64(fig)


# ---------------------------------------------------------------------------
# 1. Log Transform
# ---------------------------------------------------------------------------

def apply_log_transform(filename, c=1.0):
    """
    Apply the log intensity transformation  s = c * log(1 + r).

    The result is normalized to the full [0, 255] range so that the
    constant *c* controls relative weighting rather than absolute scale.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    c : float
        Scaling constant (default 1.0).

    Returns
    -------
    dict with keys: original, result, plot, formula, c_value, stats.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    c = float(c)
    r = img.astype(np.float64)

    # Apply transform
    s = c * np.log1p(r)  # log1p(x) == log(1 + x), numerically stable

    # Normalize to 0-255
    s_max = s.max()
    if s_max > 0:
        s = (s / s_max) * 255.0
    result = np.clip(s, 0, 255).astype(np.uint8)

    # Build transform curve for plotting
    r_curve = np.arange(0, 256, dtype=np.float64)
    s_curve = c * np.log1p(r_curve)
    s_curve_max = s_curve.max()
    if s_curve_max > 0:
        s_curve = (s_curve / s_curve_max) * 255.0

    plot_b64 = _make_transform_plot(
        r_curve, s_curve,
        title=f"Log Transform: s = c * log(1 + r)  [c = {c}]",
        label="Log curve",
    )

    return {
        "original": image_to_base64_png(img),
        "result": image_to_base64_png(result),
        "plot": plot_b64,
        "formula": "s = c * log(1 + r), normalized to [0, 255]",
        "c_value": c,
        "stats": {
            "before": _image_stats(img),
            "after": _image_stats(result),
        },
    }


# ---------------------------------------------------------------------------
# 2. Gamma (Power-Law) Transform
# ---------------------------------------------------------------------------

def apply_gamma_transform(filename, gamma=1.0, c=1.0):
    """
    Apply the power-law (gamma) transformation  s = c * r^gamma.

    Input intensities are normalized to [0, 1] before exponentiation,
    then scaled back to [0, 255].

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    gamma : float
        Exponent (default 1.0 = identity).
    c : float
        Scaling constant (default 1.0).

    Returns
    -------
    dict with keys: original, result, plot, formula, gamma, c_value, stats.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    gamma = float(gamma)
    c = float(c)

    r = img.astype(np.float64) / 255.0
    s = c * np.power(r, gamma)
    s = np.clip(s * 255.0, 0, 255).astype(np.uint8)

    # Transform curve
    r_curve = np.arange(0, 256, dtype=np.float64) / 255.0
    s_curve = c * np.power(r_curve, gamma) * 255.0
    s_curve = np.clip(s_curve, 0, 255)

    plot_b64 = _make_transform_plot(
        r_curve * 255.0, s_curve,
        title=f"Gamma Transform: s = c * r^{gamma}  [c = {c}]",
        label=f"\u03b3 = {gamma}",
    )

    return {
        "original": image_to_base64_png(img),
        "result": image_to_base64_png(s),
        "plot": plot_b64,
        "formula": "s = c * r^\u03b3  (r normalized to [0,1], then scaled to [0,255])",
        "gamma": gamma,
        "c_value": c,
        "stats": {
            "before": _image_stats(img),
            "after": _image_stats(s),
        },
    }


# ---------------------------------------------------------------------------
# 3. Contrast Stretching (Piecewise Linear)
# ---------------------------------------------------------------------------

def apply_contrast_stretch(filename, r1=50, s1=0, r2=200, s2=255):
    """
    Apply piecewise-linear contrast stretching with two breakpoints.

    Three segments:
        [0, r1]     -> [0, s1]
        [r1, r2]    -> [s1, s2]
        [r2, 255]   -> [s2, 255]

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    r1, s1 : int
        First breakpoint (input, output).
    r2, s2 : int
        Second breakpoint (input, output).

    Returns
    -------
    dict with keys: original, result, plot, breakpoints, stats.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    r1, s1, r2, s2 = int(r1), int(s1), int(r2), int(s2)

    # Enforce ordering constraints
    r1 = max(0, min(r1, 254))
    r2 = max(r1 + 1, min(r2, 255))
    s1 = max(0, min(s1, 255))
    s2 = max(0, min(s2, 255))

    # Build the lookup table via piecewise interpolation
    lut = np.zeros(256, dtype=np.float64)

    # Segment 1: [0, r1] -> [0, s1]
    if r1 > 0:
        lut[0:r1 + 1] = np.linspace(0, s1, r1 + 1)
    else:
        lut[0] = s1

    # Segment 2: [r1, r2] -> [s1, s2]
    seg2_len = r2 - r1 + 1
    lut[r1:r2 + 1] = np.linspace(s1, s2, seg2_len)

    # Segment 3: [r2, 255] -> [s2, 255]
    seg3_len = 255 - r2 + 1
    if seg3_len > 1:
        lut[r2:256] = np.linspace(s2, 255, seg3_len)
    else:
        lut[255] = 255

    lut = np.clip(lut, 0, 255).astype(np.uint8)
    result = lut[img]

    # Plot the piecewise curve
    fig, ax = plt.subplots(1, 1, figsize=(5, 4))
    r_vals = np.arange(256)
    ax.plot(r_vals, lut, color='#e74c3c', linewidth=2, label='Stretch curve')
    ax.plot([0, 255], [0, 255], 'k--', linewidth=0.8, alpha=0.4,
            label='Identity')
    ax.plot(r1, s1, 'bo', markersize=8, zorder=5, label=f'({r1}, {s1})')
    ax.plot(r2, s2, 'go', markersize=8, zorder=5, label=f'({r2}, {s2})')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_xlabel('Input Intensity (r)', fontsize=10)
    ax.set_ylabel('Output Intensity (s)', fontsize=10)
    ax.set_title('Piecewise-Linear Contrast Stretch', fontsize=11,
                 fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plot_b64 = fig_to_base64(fig)

    return {
        "original": image_to_base64_png(img),
        "result": image_to_base64_png(result),
        "plot": plot_b64,
        "breakpoints": {
            "r1": r1, "s1": s1,
            "r2": r2, "s2": s2,
        },
        "stats": {
            "before": _image_stats(img),
            "after": _image_stats(result),
        },
    }


# ---------------------------------------------------------------------------
# 4. Intensity Negation
# ---------------------------------------------------------------------------

def apply_intensity_negation(filename):
    """
    Apply intensity negation  s = 255 - r.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.

    Returns
    -------
    dict with keys: original, result, stats.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    result = (255 - img).astype(np.uint8)

    return {
        "original": image_to_base64_png(img),
        "result": image_to_base64_png(result),
        "stats": {
            "before": _image_stats(img),
            "after": _image_stats(result),
        },
    }


# ---------------------------------------------------------------------------
# 5. Bit-Plane Slicing
# ---------------------------------------------------------------------------

def apply_bit_plane_slice(filename):
    """
    Extract all 8 bit planes and build progressive MSB-to-LSB reconstructions.

    Bit plane *k* is obtained by masking the image with 2^k and normalizing
    the result to {0, 255}.  Progressive reconstruction adds planes from
    MSB (bit 7) downward.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.

    Returns
    -------
    dict with keys: original, planes (list of 8 dicts), reconstructions
    (list of dicts with progressive reconstruction from MSB to LSB).
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    planes = []
    for bit in range(8):
        mask = 1 << bit
        plane = ((img & mask) >> bit) * 255  # binary {0, 255}
        plane = plane.astype(np.uint8)
        ones_count = int(np.count_nonzero(plane))
        total = int(plane.size)
        planes.append({
            "bit": bit,
            "image": image_to_base64_png(plane),
            "info": (
                f"Bit {bit} (weight {mask}): "
                f"{ones_count} of {total} pixels are 1 "
                f"({round(ones_count / total * 100, 1)}%)"
            ),
        })

    # Progressive reconstruction from MSB (bit 7) to LSB (bit 0)
    reconstructions = []
    accumulated = np.zeros_like(img, dtype=np.uint8)
    for bit in range(7, -1, -1):
        mask = 1 << bit
        plane_values = img & mask  # keeps original weighted contribution
        accumulated = accumulated | plane_values
        # Normalize to full 0-255 range for display
        display = accumulated.copy()
        if display.max() > 0:
            display = ((display.astype(np.float64) / display.max()) * 255).astype(np.uint8)
        bits_used = list(range(7, bit - 1, -1))
        reconstructions.append({
            "bits_used": bits_used,
            "image": image_to_base64_png(accumulated),
        })

    return {
        "original": image_to_base64_png(img),
        "planes": planes,
        "reconstructions": reconstructions,
    }


# ---------------------------------------------------------------------------
# 6. Thresholding
# ---------------------------------------------------------------------------

def apply_thresholding(filename, threshold=128):
    """
    Apply binary thresholding: pixels >= threshold become 255, else 0.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    threshold : int
        Threshold value in [0, 255].

    Returns
    -------
    dict with keys: original, result, threshold, stats.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    threshold = int(max(0, min(255, threshold)))
    result = np.where(img >= threshold, np.uint8(255), np.uint8(0))
    result = result.astype(np.uint8)

    above = int(np.count_nonzero(result))
    total = int(result.size)

    return {
        "original": image_to_base64_png(img),
        "result": image_to_base64_png(result),
        "threshold": threshold,
        "stats": {
            "before": _image_stats(img),
            "after": _image_stats(result),
            "pixels_above_threshold": above,
            "pixels_below_threshold": total - above,
            "percentage_above": round(above / total * 100, 2),
        },
    }


# ---------------------------------------------------------------------------
# 7. Gamma Comparison Grid
# ---------------------------------------------------------------------------

def generate_intensity_comparison(filename, gamma_values=None):
    """
    Create a grid figure showing the same image at many gamma values.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    gamma_values : list of float or None
        Gamma exponents to display. Defaults to a representative set
        spanning dark-expansion through bright-expansion.

    Returns
    -------
    str
        Base64-encoded PNG of the comparison grid.
    None if the image cannot be loaded.
    """
    if gamma_values is None:
        gamma_values = [0.04, 0.1, 0.2, 0.4, 0.67, 1.0,
                        1.5, 2.5, 5.0, 10.0, 25.0]

    img = load_image(filename)
    if img is None:
        return None

    n = len(gamma_values)
    ncols = min(4, n)
    nrows = (n + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(4 * ncols, 4 * nrows))
    fig.suptitle('Gamma (\u03b3) Correction Comparison', fontsize=14,
                 fontweight='bold', y=1.01)

    axes_flat = np.array(axes).flatten() if n > 1 else [axes]

    r = img.astype(np.float64) / 255.0

    for idx, gamma in enumerate(gamma_values):
        s = np.power(r, gamma)
        s = np.clip(s * 255.0, 0, 255).astype(np.uint8)
        axes_flat[idx].imshow(s, cmap='gray', vmin=0, vmax=255)
        axes_flat[idx].set_title(f'\u03b3 = {gamma}', fontsize=10)
        axes_flat[idx].axis('off')

    # Hide unused subplots
    for idx in range(n, len(axes_flat)):
        axes_flat[idx].axis('off')

    fig.tight_layout()
    return fig_to_base64(fig, dpi=100)


# ---------------------------------------------------------------------------
# 8. Educational Transform Curves
# ---------------------------------------------------------------------------

def get_transform_curves():
    """
    Produce a single figure with log, multiple gamma, negation, and
    contrast-stretch curves for side-by-side educational comparison.

    Returns
    -------
    str
        Base64-encoded PNG of the curves figure.
    """
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    fig.suptitle('Intensity Transformation Functions (Chapter 3.2)',
                 fontsize=13, fontweight='bold')

    r = np.arange(0, 256, dtype=np.float64)

    # ---- Panel 1: Log Transform ----
    ax = axes[0, 0]
    s_log = np.log1p(r)
    s_log = (s_log / s_log.max()) * 255.0
    ax.plot(r, s_log, color='#2980b9', linewidth=2, label='s = c * log(1+r)')
    ax.plot([0, 255], [0, 255], 'k--', linewidth=0.8, alpha=0.4,
            label='Identity')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_xlabel('Input (r)', fontsize=9)
    ax.set_ylabel('Output (s)', fontsize=9)
    ax.set_title('Log Transform', fontsize=10, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 2: Gamma Curves ----
    ax = axes[0, 1]
    gammas = [0.04, 0.1, 0.2, 0.4, 0.67, 1.0, 1.5, 2.5, 5.0, 10.0, 25.0]
    cmap = plt.get_cmap('coolwarm')
    for i, g in enumerate(gammas):
        color = cmap(i / (len(gammas) - 1))
        r_norm = r / 255.0
        s_gamma = np.power(r_norm, g) * 255.0
        lw = 2.5 if g == 1.0 else 1.4
        ls = '--' if g == 1.0 else '-'
        ax.plot(r, s_gamma, color=color, linewidth=lw, linestyle=ls,
                label=f'\u03b3={g}')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_xlabel('Input (r)', fontsize=9)
    ax.set_ylabel('Output (s)', fontsize=9)
    ax.set_title('Gamma (Power-Law) Transforms', fontsize=10,
                 fontweight='bold')
    ax.legend(fontsize=7, ncol=2, loc='lower right')
    ax.grid(True, alpha=0.3)

    # ---- Panel 3: Negation ----
    ax = axes[1, 0]
    s_neg = 255.0 - r
    ax.plot(r, s_neg, color='#c0392b', linewidth=2, label='s = 255 - r')
    ax.plot([0, 255], [0, 255], 'k--', linewidth=0.8, alpha=0.4,
            label='Identity')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_xlabel('Input (r)', fontsize=9)
    ax.set_ylabel('Output (s)', fontsize=9)
    ax.set_title('Intensity Negation', fontsize=10, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # ---- Panel 4: Contrast Stretching Examples ----
    ax = axes[1, 1]
    stretch_configs = [
        (50, 0, 200, 255, '#27ae60', 'Mild stretch'),
        (100, 0, 150, 255, '#8e44ad', 'Strong stretch'),
        (128, 0, 129, 255, '#d35400', 'Near-threshold'),
    ]
    for r1, s1, r2, s2, color, label in stretch_configs:
        lut = np.zeros(256, dtype=np.float64)
        if r1 > 0:
            lut[0:r1 + 1] = np.linspace(0, s1, r1 + 1)
        else:
            lut[0] = s1
        lut[r1:r2 + 1] = np.linspace(s1, s2, r2 - r1 + 1)
        seg3_len = 255 - r2 + 1
        if seg3_len > 1:
            lut[r2:256] = np.linspace(s2, 255, seg3_len)
        else:
            lut[255] = 255
        ax.plot(r, np.clip(lut, 0, 255), color=color, linewidth=1.8,
                label=label)
    ax.plot([0, 255], [0, 255], 'k--', linewidth=0.8, alpha=0.4,
            label='Identity')
    ax.set_xlim(0, 255)
    ax.set_ylim(0, 255)
    ax.set_xlabel('Input (r)', fontsize=9)
    ax.set_ylabel('Output (s)', fontsize=9)
    ax.set_title('Contrast Stretching (Piecewise Linear)', fontsize=10,
                 fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    return fig_to_base64(fig)
