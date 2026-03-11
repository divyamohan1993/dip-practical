"""
Practical 3 -- Histogram Equalization and CLAHE processing functions.
Covers histogram equalization, CLAHE, histogram matching (specification),
local histogram statistics, educational walkthrough, and raw histogram data.

Reference: Gonzalez & Woods, Digital Image Processing, Chapter 3.3.
"""

import cv2
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
# Helper: compute image statistics dict
# ---------------------------------------------------------------------------

def _image_stats(img):
    """Return a compact statistics dict for a grayscale image."""
    return {
        "min": int(img.min()),
        "max": int(img.max()),
        "mean": round(float(np.mean(img)), 2),
        "std": round(float(np.std(img)), 2),
        "contrast_ratio": round(float(img.max()) / max(float(img.min()), 1.0), 4),
    }


def _plot_histogram_with_cdf(ax, img, title, color='#3498db', cdf_color='#e74c3c'):
    """
    Draw a histogram and overlaid CDF on the given axes.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Target axes.
    img : numpy.ndarray
        Grayscale uint8 image.
    title : str
        Axes title.
    color : str
        Histogram bar colour.
    cdf_color : str
        CDF line colour.
    """
    hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()

    ax.bar(range(256), hist, color=color, width=1.0, edgecolor='none', alpha=0.7)
    ax.set_xlim([0, 256])
    ax.set_xlabel('Pixel Intensity', fontsize=9)
    ax.set_ylabel('Frequency', fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.grid(True, alpha=0.3)

    # Overlay CDF on a twin axis
    cdf = np.cumsum(hist)
    cdf_normalised = cdf / cdf[-1] if cdf[-1] > 0 else cdf
    ax2 = ax.twinx()
    ax2.plot(cdf_normalised, color=cdf_color, linewidth=1.5, label='CDF')
    ax2.set_ylabel('CDF', fontsize=9, color=cdf_color)
    ax2.set_ylim([0, 1.05])
    ax2.tick_params(axis='y', labelcolor=cdf_color)


# ---------------------------------------------------------------------------
# 1. Histogram Equalization
# ---------------------------------------------------------------------------

def compute_histogram_equalization(filename):
    """
    Apply global histogram equalization to a grayscale image.

    Returns a dict with original/equalized images, their histograms with CDF,
    a 2x2 comparison plot, the first 32 entries of the intensity mapping table,
    and before/after statistics.  Returns None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    equalized = cv2.equalizeHist(img)

    # --- Individual histogram plots ---
    fig_orig, ax_orig = plt.subplots(figsize=(6, 3.5))
    _plot_histogram_with_cdf(ax_orig, img, 'Original Histogram + CDF')
    fig_orig.tight_layout()
    original_histogram = fig_to_base64(fig_orig)

    fig_eq, ax_eq = plt.subplots(figsize=(6, 3.5))
    _plot_histogram_with_cdf(ax_eq, equalized, 'Equalized Histogram + CDF', color='#2ecc71')
    fig_eq.tight_layout()
    equalized_histogram = fig_to_base64(fig_eq)

    # --- 2x2 comparison plot ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Histogram Equalization', fontsize=14, fontweight='bold', y=0.98)

    axes[0, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title('Original Image', fontsize=10)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(equalized, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title('Equalized Image', fontsize=10)
    axes[0, 1].axis('off')

    _plot_histogram_with_cdf(axes[1, 0], img, 'Original Histogram + CDF')
    _plot_histogram_with_cdf(axes[1, 1], equalized, 'Equalized Histogram + CDF',
                             color='#2ecc71')

    fig.tight_layout()
    comparison_plot = fig_to_base64(fig)

    # --- Mapping table (first 32 entries) ---
    # Build the mapping via the standard equalization formula:
    #   s_k = round( (L-1) * CDF(r_k) )
    hist_orig = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
    cdf = np.cumsum(hist_orig)
    cdf_min = cdf[cdf > 0].min() if np.any(cdf > 0) else 0
    total = img.size
    L = 256
    mapping = np.round((cdf - cdf_min) / max(total - cdf_min, 1) * (L - 1)).astype(int)
    mapping = np.clip(mapping, 0, 255)

    mapping_table = [
        {"input": int(i), "output": int(mapping[i])}
        for i in range(32)
    ]

    # --- Statistics ---
    stats = {
        "before": _image_stats(img),
        "after": _image_stats(equalized),
    }

    return {
        "original": image_to_base64_png(img),
        "equalized": image_to_base64_png(equalized),
        "original_histogram": original_histogram,
        "equalized_histogram": equalized_histogram,
        "comparison_plot": comparison_plot,
        "mapping_table": mapping_table,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# 2. CLAHE
# ---------------------------------------------------------------------------

def compute_clahe(filename, clip_limit=2.0, tile_size=8):
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).

    Also computes global equalization for side-by-side comparison.
    Returns a dict with original, CLAHE result, global EQ result,
    comparison plot, histogram comparison, parameters used, and statistics.
    Returns None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    clip_limit = float(clip_limit)
    tile_size = int(tile_size)

    # Global equalization for comparison
    global_eq = cv2.equalizeHist(img)

    # CLAHE
    clahe = cv2.createCLAHE(clipLimit=clip_limit,
                            tileGridSize=(tile_size, tile_size))
    clahe_result = clahe.apply(img)

    # --- 1x3 comparison plot ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Original vs Global EQ vs CLAHE', fontsize=13, fontweight='bold')

    titles = ['Original', 'Global Equalization', f'CLAHE (clip={clip_limit}, tile={tile_size})']
    images = [img, global_eq, clahe_result]
    for ax, im, title in zip(axes, images, titles):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontsize=10)
        ax.axis('off')

    fig.tight_layout()
    comparison_plot = fig_to_base64(fig)

    # --- Histogram comparison (3 side-by-side) ---
    fig_hist, axes_h = plt.subplots(1, 3, figsize=(15, 4))
    fig_hist.suptitle('Histogram Comparison', fontsize=13, fontweight='bold')

    hist_data = [
        (img, 'Original', '#3498db'),
        (global_eq, 'Global EQ', '#e74c3c'),
        (clahe_result, 'CLAHE', '#2ecc71'),
    ]
    for ax, (im, label, color) in zip(axes_h, hist_data):
        _plot_histogram_with_cdf(ax, im, f'{label} Histogram + CDF', color=color)

    fig_hist.tight_layout()
    histogram_comparison = fig_to_base64(fig_hist)

    # --- Statistics ---
    stats = {
        "original": _image_stats(img),
        "global_eq": _image_stats(global_eq),
        "clahe": _image_stats(clahe_result),
    }

    return {
        "original": image_to_base64_png(img),
        "clahe_result": image_to_base64_png(clahe_result),
        "global_eq_result": image_to_base64_png(global_eq),
        "comparison_plot": comparison_plot,
        "histogram_comparison": histogram_comparison,
        "clip_limit": clip_limit,
        "tile_size": tile_size,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# 3. Histogram Matching (Specification)
# ---------------------------------------------------------------------------

def compute_histogram_matching(source_filename, target_filename):
    """
    Transform the source image so its histogram matches the target's histogram.

    Uses the standard histogram specification algorithm:
        1. Compute CDFs of source and target.
        2. For each source intensity, find the target intensity whose CDF
           value is closest.

    Returns a dict with source, target, matched images, histogram plot,
    and statistics.  Returns None if either image cannot be loaded.
    """
    src = load_image(source_filename)
    tgt = load_image(target_filename)
    if src is None or tgt is None:
        return None

    # --- Build CDFs ---
    src_hist = cv2.calcHist([src], [0], None, [256], [0, 256]).flatten()
    tgt_hist = cv2.calcHist([tgt], [0], None, [256], [0, 256]).flatten()

    src_cdf = np.cumsum(src_hist).astype(np.float64)
    tgt_cdf = np.cumsum(tgt_hist).astype(np.float64)

    # Normalise CDFs to [0, 1]
    src_cdf /= src_cdf[-1] if src_cdf[-1] > 0 else 1.0
    tgt_cdf /= tgt_cdf[-1] if tgt_cdf[-1] > 0 else 1.0

    # --- Build mapping: for each source level find closest target CDF value ---
    mapping = np.zeros(256, dtype=np.uint8)
    for src_val in range(256):
        # Find the target intensity whose CDF is closest to src CDF
        diff = np.abs(tgt_cdf - src_cdf[src_val])
        mapping[src_val] = np.argmin(diff)

    # Apply the lookup table
    matched = mapping[src]

    # --- Histogram plot: 3 histograms ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle('Histogram Matching (Specification)', fontsize=13, fontweight='bold')

    _plot_histogram_with_cdf(axes[0], src, 'Source Histogram + CDF', color='#3498db')
    _plot_histogram_with_cdf(axes[1], tgt, 'Target Histogram + CDF', color='#e74c3c')
    _plot_histogram_with_cdf(axes[2], matched, 'Matched Histogram + CDF', color='#2ecc71')

    fig.tight_layout()
    histogram_plot = fig_to_base64(fig)

    # --- Statistics ---
    stats = {
        "source": _image_stats(src),
        "target": _image_stats(tgt),
        "matched": _image_stats(matched),
    }

    return {
        "source": image_to_base64_png(src),
        "target": image_to_base64_png(tgt),
        "matched": image_to_base64_png(matched),
        "histogram_plot": histogram_plot,
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# 4. Local Histogram Statistics
# ---------------------------------------------------------------------------

def compute_local_histogram_stats(filename, window_size=3):
    """
    Compute local histogram statistics (mean and standard deviation)
    using a sliding window and produce a locally enhanced image.

    Enhancement rule (Gonzalez & Woods 3.3.4):
        If the local mean is below the global mean AND the local std is
        within a specified range, multiply the pixel by a gain factor to
        brighten dark low-contrast regions.

    Returns a dict with original, local mean, local std, enhanced images,
    a 2x2 plot, and the window size used.  Returns None on failure.
    """
    img = load_image(filename)
    if img is None:
        return None

    window_size = max(3, int(window_size))
    # Ensure odd kernel size
    if window_size % 2 == 0:
        window_size += 1

    img_float = img.astype(np.float64)

    # Local mean via box filter
    local_mean = cv2.blur(img_float, (window_size, window_size))

    # Local standard deviation: std = sqrt( E[X^2] - (E[X])^2 )
    local_sq_mean = cv2.blur(img_float ** 2, (window_size, window_size))
    local_variance = np.maximum(local_sq_mean - local_mean ** 2, 0.0)
    local_std = np.sqrt(local_variance)

    # --- Local enhancement ---
    global_mean = np.mean(img_float)
    global_std = np.std(img_float)

    gain = 4.0  # amplification factor for qualifying pixels
    k0 = 0.4   # local mean must be below k0 * global_mean
    k1 = 0.02  # local std lower bound (fraction of global std)
    k2 = 0.4   # local std upper bound (fraction of global std)

    # Build mask of pixels that qualify for enhancement
    mean_mask = local_mean <= k0 * global_mean
    std_mask = (local_std >= k1 * global_std) & (local_std <= k2 * global_std)
    enhance_mask = mean_mask & std_mask

    enhanced = img_float.copy()
    enhanced[enhance_mask] = np.clip(gain * enhanced[enhance_mask], 0, 255)
    enhanced = enhanced.astype(np.uint8)

    # Normalise local_mean and local_std to uint8 for display
    local_mean_display = cv2.normalize(local_mean, None, 0, 255,
                                       cv2.NORM_MINMAX).astype(np.uint8)
    local_std_display = cv2.normalize(local_std, None, 0, 255,
                                      cv2.NORM_MINMAX).astype(np.uint8)

    # --- 2x2 plot ---
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    fig.suptitle(f'Local Histogram Statistics (window={window_size})',
                 fontsize=13, fontweight='bold', y=0.98)

    panels = [
        (img, 'Original'),
        (local_mean_display, 'Local Mean'),
        (local_std_display, 'Local Std Dev'),
        (enhanced, 'Locally Enhanced'),
    ]
    for ax, (im, title) in zip(axes.flat, panels):
        ax.imshow(im, cmap='gray', vmin=0, vmax=255)
        ax.set_title(title, fontsize=10)
        ax.axis('off')

    fig.tight_layout()
    plot = fig_to_base64(fig)

    return {
        "original": image_to_base64_png(img),
        "local_mean": image_to_base64_png(local_mean_display),
        "local_std": image_to_base64_png(local_std_display),
        "enhanced": image_to_base64_png(enhanced),
        "plot": plot,
        "window_size": window_size,
    }


# ---------------------------------------------------------------------------
# 5. Educational Step-by-Step Walkthrough
# ---------------------------------------------------------------------------

def generate_histogram_walkthrough(filename):
    """
    Produce an educational walkthrough of the histogram equalization process.

    Each step contains a title, a description, and either an image or a plot
    encoded as base64.  Steps cover:
        1. Original image and its histogram
        2. Probability Density Function (PDF)
        3. Cumulative Distribution Function (CDF)
        4. Mapping formula derivation
        5. Mapping curve visualisation
        6. Final equalized result

    Returns a dict with a ``steps`` list.  Returns None on failure.
    """
    img = load_image(filename)
    if img is None:
        return None

    steps = []

    # ---- Step 1: Original image + histogram ----
    fig1, axes1 = plt.subplots(1, 2, figsize=(11, 4))
    axes1[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes1[0].set_title('Original Image', fontsize=10)
    axes1[0].axis('off')

    hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
    axes1[1].bar(range(256), hist, color='#3498db', width=1.0, edgecolor='none')
    axes1[1].set_xlim([0, 256])
    axes1[1].set_xlabel('Intensity')
    axes1[1].set_ylabel('Pixel Count')
    axes1[1].set_title('Histogram h(r_k)', fontsize=10)
    axes1[1].grid(True, alpha=0.3)
    fig1.tight_layout()

    steps.append({
        "title": "Step 1: Original Image and Histogram",
        "description": (
            "The histogram h(r_k) counts the number of pixels at each "
            "intensity level r_k (0-255). A narrow or skewed histogram "
            "indicates poor contrast utilisation of the available dynamic range."
        ),
        "plot": fig_to_base64(fig1),
    })

    # ---- Step 2: PDF ----
    total_pixels = img.size
    pdf = hist / total_pixels

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    ax2.bar(range(256), pdf, color='#9b59b6', width=1.0, edgecolor='none')
    ax2.set_xlim([0, 256])
    ax2.set_xlabel('Intensity r_k')
    ax2.set_ylabel('p(r_k)')
    ax2.set_title('Probability Density Function (PDF)', fontsize=11)
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()

    steps.append({
        "title": "Step 2: Probability Density Function (PDF)",
        "description": (
            "The PDF is the normalised histogram: p(r_k) = h(r_k) / N, where "
            "N is the total number of pixels. Each bar now represents the "
            "probability of a pixel having intensity r_k. The sum of all bars "
            "equals 1.0."
        ),
        "plot": fig_to_base64(fig2),
    })

    # ---- Step 3: CDF ----
    cdf = np.cumsum(pdf)

    fig3, ax3 = plt.subplots(figsize=(7, 4))
    ax3.plot(range(256), cdf, color='#e74c3c', linewidth=2)
    ax3.fill_between(range(256), cdf, alpha=0.15, color='#e74c3c')
    ax3.set_xlim([0, 256])
    ax3.set_ylim([0, 1.05])
    ax3.set_xlabel('Intensity r_k')
    ax3.set_ylabel('CDF(r_k)')
    ax3.set_title('Cumulative Distribution Function (CDF)', fontsize=11)
    ax3.grid(True, alpha=0.3)
    fig3.tight_layout()

    steps.append({
        "title": "Step 3: Cumulative Distribution Function (CDF)",
        "description": (
            "The CDF is the running sum of the PDF: CDF(r_k) = sum of p(r_j) "
            "for j = 0 to k. It is a monotonically non-decreasing function "
            "from 0 to 1. The CDF is the core of the equalization transform -- "
            "it maps input intensities to output intensities."
        ),
        "plot": fig_to_base64(fig3),
    })

    # ---- Step 4: Mapping formula ----
    # Build mapping
    cdf_raw = np.cumsum(hist)
    cdf_min = cdf_raw[cdf_raw > 0].min() if np.any(cdf_raw > 0) else 0
    L = 256
    mapping = np.round((cdf_raw - cdf_min) / max(total_pixels - cdf_min, 1) * (L - 1))
    mapping = np.clip(mapping, 0, 255).astype(int)

    # Show a small sample table as a plot
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.axis('off')

    sample_indices = [0, 16, 32, 64, 96, 128, 160, 192, 224, 255]
    table_data = [
        [str(i), f"{hist[i]:.0f}", f"{pdf[i]:.6f}", f"{cdf[i]:.6f}", str(mapping[i])]
        for i in sample_indices
    ]
    col_labels = ['r_k', 'h(r_k)', 'p(r_k)', 'CDF(r_k)', 's_k (output)']
    table = ax4.table(cellText=table_data, colLabels=col_labels,
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.6)
    ax4.set_title(
        'Mapping Formula:  s_k = round( (L-1) * (CDF(r_k) - CDF_min) / (N - CDF_min) )',
        fontsize=10, fontweight='bold', pad=20,
    )
    fig4.tight_layout()

    steps.append({
        "title": "Step 4: Mapping Formula",
        "description": (
            "The equalization transform maps each input intensity r_k to an "
            "output s_k using: s_k = round( (L-1) * (CDF(r_k) - CDF_min) / "
            "(N - CDF_min) ), where L=256 is the number of grey levels, N is "
            "the total pixel count, and CDF_min is the minimum non-zero CDF "
            "value. This stretches the CDF to use the full [0, 255] range."
        ),
        "plot": fig_to_base64(fig4),
    })

    # ---- Step 5: Mapping curve ----
    fig5, ax5 = plt.subplots(figsize=(6, 5))
    ax5.plot(range(256), mapping, color='#2c3e50', linewidth=2)
    ax5.plot([0, 255], [0, 255], 'k--', linewidth=0.8, alpha=0.4, label='Identity')
    ax5.set_xlim([0, 255])
    ax5.set_ylim([0, 255])
    ax5.set_xlabel('Input Intensity r_k')
    ax5.set_ylabel('Output Intensity s_k')
    ax5.set_title('Intensity Mapping Curve (Transfer Function)', fontsize=11)
    ax5.legend(fontsize=9)
    ax5.set_aspect('equal')
    ax5.grid(True, alpha=0.3)
    fig5.tight_layout()

    steps.append({
        "title": "Step 5: Mapping Curve (Transfer Function)",
        "description": (
            "The transfer function shows how each input intensity is remapped. "
            "The dashed line is the identity (no change). Where the curve is "
            "steeper than the identity, contrast is expanded for those "
            "intensity ranges. Where it is flatter, contrast is compressed. "
            "An ideal equalization produces a mapping that is as close to a "
            "straight line from (0,0) to (255,255) as the discrete histogram "
            "allows."
        ),
        "plot": fig_to_base64(fig5),
    })

    # ---- Step 6: Final result ----
    equalized = cv2.equalizeHist(img)

    fig6, axes6 = plt.subplots(1, 2, figsize=(11, 4))
    axes6[0].imshow(equalized, cmap='gray', vmin=0, vmax=255)
    axes6[0].set_title('Equalized Image', fontsize=10)
    axes6[0].axis('off')

    eq_hist = cv2.calcHist([equalized], [0], None, [256], [0, 256]).flatten()
    axes6[1].bar(range(256), eq_hist, color='#2ecc71', width=1.0, edgecolor='none')
    axes6[1].set_xlim([0, 256])
    axes6[1].set_xlabel('Intensity')
    axes6[1].set_ylabel('Pixel Count')
    axes6[1].set_title('Equalized Histogram', fontsize=10)
    axes6[1].grid(True, alpha=0.3)
    fig6.tight_layout()

    steps.append({
        "title": "Step 6: Final Equalized Result",
        "description": (
            "After applying the mapping to every pixel, the equalized image "
            "has a histogram that approximates a uniform distribution. The "
            "result uses the full dynamic range [0, 255], improving the "
            "perceived contrast. Note: because of the discrete nature of "
            "digital images, the equalized histogram will not be perfectly "
            "flat -- some bins will be taller than others."
        ),
        "plot": fig_to_base64(fig6),
    })

    return {"steps": steps}


# ---------------------------------------------------------------------------
# 6. Raw Histogram Data
# ---------------------------------------------------------------------------

def get_histogram_data(filename):
    """
    Return the raw histogram (256 bins), normalised CDF, and basic
    statistics for a grayscale image as JSON-friendly structures.

    Returns a dict with ``histogram`` (list of 256 ints),
    ``cdf`` (list of 256 floats in [0, 1]), and ``stats``.
    Returns None on failure.
    """
    img = load_image(filename)
    if img is None:
        return None

    hist = cv2.calcHist([img], [0], None, [256], [0, 256]).flatten()
    cdf = np.cumsum(hist).astype(np.float64)
    cdf_normalised = cdf / cdf[-1] if cdf[-1] > 0 else cdf

    return {
        "histogram": [int(v) for v in hist],
        "cdf": [round(float(v), 6) for v in cdf_normalised],
        "stats": _image_stats(img),
    }
