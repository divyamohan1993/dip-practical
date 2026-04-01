"""Practical 6: Histogram Matching (Specification)."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


def _histogram_match(source, target):
    """Match source histogram to target histogram via CDF inversion."""
    src_hist, _ = np.histogram(source.ravel(), bins=256, range=(0, 256))
    tgt_hist, _ = np.histogram(target.ravel(), bins=256, range=(0, 256))

    src_cdf = np.cumsum(src_hist).astype(np.float64)
    src_cdf /= src_cdf[-1]
    tgt_cdf = np.cumsum(tgt_hist).astype(np.float64)
    tgt_cdf /= tgt_cdf[-1]

    # Build lookup: for each source intensity, find closest target CDF value
    lut = np.zeros(256, dtype=np.uint8)
    for r in range(256):
        lut[r] = np.argmin(np.abs(tgt_cdf - src_cdf[r]))

    return lut[source]


def compute_source_histogram(filename, chapter='CH02'):
    """Load source image and show its histogram."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Source Image")
    axes[0].axis('off')

    axes[1].hist(img.ravel(), bins=256, range=(0, 256), color='steelblue', alpha=0.85, edgecolor='none')
    axes[1].set_title("Source Histogram")
    axes[1].set_xlabel("Pixel Intensity")
    axes[1].set_ylabel("Frequency")
    axes[1].set_xlim(0, 255)

    fig.suptitle(f"Source: {filename}", fontsize=13, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": filename}


def compute_equalize_baseline(filename, chapter='CH02'):
    """Equalize the source as a baseline for comparison."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    equalized = cv2.equalizeHist(img)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes[0, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Original Source")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(equalized, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title("Equalized (Uniform Target)")
    axes[0, 1].axis('off')

    axes[1, 0].hist(img.ravel(), bins=256, range=(0, 256), color='steelblue', alpha=0.85, edgecolor='none')
    axes[1, 0].set_title("Original Histogram")
    axes[1, 0].set_xlabel("Pixel Intensity")
    axes[1, 0].set_ylabel("Frequency")
    axes[1, 0].set_xlim(0, 255)

    axes[1, 1].hist(equalized.ravel(), bins=256, range=(0, 256), color='darkorange', alpha=0.85, edgecolor='none')
    axes[1, 1].set_title("Equalized Histogram")
    axes[1, 1].set_xlabel("Pixel Intensity")
    axes[1, 1].set_ylabel("Frequency")
    axes[1, 1].set_xlim(0, 255)

    fig.suptitle("Step 1: Histogram Equalization (Baseline)", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": filename}


def compute_matching(src_filename, tgt_filename, src_chapter='CH02', tgt_chapter='CH02'):
    """Match source histogram to target image histogram."""
    src = load_image(src_filename, src_chapter)
    tgt = load_image(tgt_filename, tgt_chapter)
    if src is None or tgt is None:
        return None

    matched = _histogram_match(src, tgt)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].imshow(src, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Source Image")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(tgt, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title("Target (Reference) Image")
    axes[0, 1].axis('off')

    axes[0, 2].imshow(matched, cmap='gray', vmin=0, vmax=255)
    axes[0, 2].set_title("Matched Result")
    axes[0, 2].axis('off')

    axes[1, 0].hist(src.ravel(), bins=256, range=(0, 256), color='steelblue', alpha=0.85, edgecolor='none')
    axes[1, 0].set_title("Source Histogram")
    axes[1, 0].set_xlabel("Pixel Intensity")
    axes[1, 0].set_xlim(0, 255)

    axes[1, 1].hist(tgt.ravel(), bins=256, range=(0, 256), color='seagreen', alpha=0.85, edgecolor='none')
    axes[1, 1].set_title("Target Histogram")
    axes[1, 1].set_xlabel("Pixel Intensity")
    axes[1, 1].set_xlim(0, 255)

    axes[1, 2].hist(matched.ravel(), bins=256, range=(0, 256), color='darkorange', alpha=0.85, edgecolor='none')
    axes[1, 2].set_title("Matched Histogram")
    axes[1, 2].set_xlabel("Pixel Intensity")
    axes[1, 2].set_xlim(0, 255)

    fig.suptitle("Histogram Matching: Source → Target", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "src_filename": src_filename,
        "tgt_filename": tgt_filename,
    }


def compute_multi_target(src_filename, tgt_filenames, src_chapter='CH02', tgt_chapter='CH02'):
    """Match one source to multiple targets (equalized, dark, bright)."""
    src = load_image(src_filename, src_chapter)
    if src is None:
        return None

    equalized = cv2.equalizeHist(src)

    targets = [("Equalized", equalized)]
    for item in tgt_filenames:
        fn = item.get('filename', '')
        ch = item.get('chapter', 'CH02')
        label = item.get('label', fn[:25])
        tgt = load_image(fn, ch)
        if tgt is not None:
            targets.append((label, tgt))

    n = len(targets)
    fig, axes = plt.subplots(2, n + 1, figsize=(4 * (n + 1), 8))

    # Source column
    axes[0, 0].imshow(src, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Source")
    axes[0, 0].axis('off')
    axes[1, 0].hist(src.ravel(), bins=256, range=(0, 256), color='steelblue', alpha=0.85, edgecolor='none')
    axes[1, 0].set_title("Source Histogram")
    axes[1, 0].set_xlim(0, 255)

    colors = ['darkorange', 'crimson', 'seagreen', 'mediumpurple', 'goldenrod']
    for i, (label, tgt) in enumerate(targets):
        matched = _histogram_match(src, tgt)
        axes[0, i + 1].imshow(matched, cmap='gray', vmin=0, vmax=255)
        axes[0, i + 1].set_title(f"→ {label}")
        axes[0, i + 1].axis('off')
        c = colors[i % len(colors)]
        axes[1, i + 1].hist(matched.ravel(), bins=256, range=(0, 256), color=c, alpha=0.85, edgecolor='none')
        axes[1, i + 1].set_title(f"Matched Hist")
        axes[1, i + 1].set_xlim(0, 255)

    fig.suptitle("Histogram Matching: One Source → Multiple Targets", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": src_filename}


def compute_transfer_analysis(src_filename, tgt_filename, src_chapter='CH02', tgt_chapter='CH02'):
    """Show CDF-based mapping used in histogram matching."""
    src = load_image(src_filename, src_chapter)
    tgt = load_image(tgt_filename, tgt_chapter)
    if src is None or tgt is None:
        return None

    src_hist, _ = np.histogram(src.ravel(), bins=256, range=(0, 256))
    tgt_hist, _ = np.histogram(tgt.ravel(), bins=256, range=(0, 256))
    src_cdf = np.cumsum(src_hist).astype(np.float64)
    src_cdf /= src_cdf[-1]
    tgt_cdf = np.cumsum(tgt_hist).astype(np.float64)
    tgt_cdf /= tgt_cdf[-1]

    # Build mapping
    mapping = np.zeros(256, dtype=np.uint8)
    for r in range(256):
        mapping[r] = np.argmin(np.abs(tgt_cdf - src_cdf[r]))

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # CDF comparison
    axes[0].plot(range(256), src_cdf, color='steelblue', linewidth=2, label='Source CDF')
    axes[0].plot(range(256), tgt_cdf, color='seagreen', linewidth=2, label='Target CDF')
    axes[0].plot([0, 255], [0, 1], 'k--', alpha=0.3, label='Ideal Uniform')
    axes[0].set_title("CDF Comparison")
    axes[0].set_xlabel("Pixel Intensity")
    axes[0].set_ylabel("Cumulative Probability")
    axes[0].legend()
    axes[0].set_xlim(0, 255)
    axes[0].grid(True, alpha=0.3)

    # Transfer function (mapping)
    axes[1].plot(range(256), mapping, color='crimson', linewidth=2)
    axes[1].plot([0, 255], [0, 255], 'k--', alpha=0.3, label='Identity')
    axes[1].set_title("Transfer Function (Mapping)")
    axes[1].set_xlabel("Source Intensity (r)")
    axes[1].set_ylabel("Matched Intensity (z)")
    axes[1].legend()
    axes[1].set_xlim(0, 255)
    axes[1].set_ylim(0, 255)
    axes[1].set_aspect('equal')
    axes[1].grid(True, alpha=0.3)

    # Matched CDF vs target CDF
    matched = mapping[src.ravel()]
    matched_hist, _ = np.histogram(matched, bins=256, range=(0, 256))
    matched_cdf = np.cumsum(matched_hist).astype(np.float64)
    matched_cdf /= matched_cdf[-1]

    axes[2].plot(range(256), tgt_cdf, color='seagreen', linewidth=2, label='Target CDF')
    axes[2].plot(range(256), matched_cdf, color='darkorange', linewidth=2, linestyle='--', label='Matched CDF')
    axes[2].set_title("Verification: Matched vs Target CDF")
    axes[2].set_xlabel("Pixel Intensity")
    axes[2].set_ylabel("Cumulative Probability")
    axes[2].legend()
    axes[2].set_xlim(0, 255)
    axes[2].grid(True, alpha=0.3)

    fig.suptitle("Histogram Matching: Transfer Function Analysis", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig)}
