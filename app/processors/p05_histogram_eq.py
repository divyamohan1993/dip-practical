"""Practical 5: Histogram Equalization."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


def compute_original_histogram(filename, chapter='CH02'):
    """Plot the original image alongside its histogram."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Original Image")
    axes[0].axis('off')

    axes[1].hist(img.ravel(), bins=256, range=(0, 256), color='steelblue', alpha=0.85, edgecolor='none')
    axes[1].set_title("Original Histogram")
    axes[1].set_xlabel("Pixel Intensity")
    axes[1].set_ylabel("Frequency")
    axes[1].set_xlim(0, 255)

    fig.suptitle(f"Original Image & Histogram: {filename}", fontsize=13, fontweight='bold')
    fig.tight_layout()

    h, w = img.shape
    mean_val = float(np.mean(img))
    std_val = float(np.std(img))

    return {
        "plot": fig_to_base64(fig),
        "filename": filename,
        "properties": {
            "width": w, "height": h,
            "min": int(img.min()), "max": int(img.max()),
            "mean": round(mean_val, 2), "std": round(std_val, 2),
        },
    }


def compute_equalization(filename, chapter='CH02'):
    """Perform histogram equalization and return before/after comparison."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    equalized = cv2.equalizeHist(img)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Original Image")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(equalized, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title("Histogram Equalized Image")
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

    fig.suptitle(f"Histogram Equalization: {filename}", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "original": image_to_base64_png(img),
        "equalized": image_to_base64_png(equalized),
        "plot": fig_to_base64(fig),
        "filename": filename,
        "stats": {
            "original_mean": round(float(np.mean(img)), 2),
            "original_std": round(float(np.std(img)), 2),
            "equalized_mean": round(float(np.mean(equalized)), 2),
            "equalized_std": round(float(np.std(equalized)), 2),
        },
    }


def compute_transfer_function(filename, chapter='CH02'):
    """Show the CDF-based transfer function used in histogram equalization."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    hist, bins = np.histogram(img.ravel(), bins=256, range=(0, 256))
    pdf = hist / hist.sum()
    cdf = np.cumsum(pdf)

    equalized = cv2.equalizeHist(img)
    hist_eq, _ = np.histogram(equalized.ravel(), bins=256, range=(0, 256))
    pdf_eq = hist_eq / hist_eq.sum()
    cdf_eq = np.cumsum(pdf_eq)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Original PDF
    axes[0, 0].bar(range(256), pdf, color='steelblue', alpha=0.85, width=1.0)
    axes[0, 0].set_title("Original PDF (Normalized Histogram)")
    axes[0, 0].set_xlabel("Pixel Intensity")
    axes[0, 0].set_ylabel("Probability")
    axes[0, 0].set_xlim(0, 255)

    # Transfer function (CDF)
    axes[0, 1].plot(range(256), cdf * 255, color='crimson', linewidth=2)
    axes[0, 1].plot([0, 255], [0, 255], 'k--', alpha=0.3, label="Identity")
    axes[0, 1].set_title("Transfer Function T(r) = CDF(r) × (L−1)")
    axes[0, 1].set_xlabel("Input Intensity (r)")
    axes[0, 1].set_ylabel("Output Intensity (s)")
    axes[0, 1].legend()
    axes[0, 1].set_xlim(0, 255)
    axes[0, 1].set_ylim(0, 255)
    axes[0, 1].set_aspect('equal')
    axes[0, 1].grid(True, alpha=0.3)

    # Equalized PDF
    axes[1, 0].bar(range(256), pdf_eq, color='darkorange', alpha=0.85, width=1.0)
    axes[1, 0].set_title("Equalized PDF")
    axes[1, 0].set_xlabel("Pixel Intensity")
    axes[1, 0].set_ylabel("Probability")
    axes[1, 0].set_xlim(0, 255)

    # CDF comparison
    axes[1, 1].plot(range(256), cdf, color='steelblue', linewidth=2, label="Original CDF")
    axes[1, 1].plot(range(256), cdf_eq, color='darkorange', linewidth=2, label="Equalized CDF")
    axes[1, 1].plot([0, 255], [0, 1], 'k--', alpha=0.3, label="Ideal Uniform CDF")
    axes[1, 1].set_title("CDF Comparison")
    axes[1, 1].set_xlabel("Pixel Intensity")
    axes[1, 1].set_ylabel("Cumulative Probability")
    axes[1, 1].legend()
    axes[1, 1].set_xlim(0, 255)
    axes[1, 1].set_ylim(0, 1.05)
    axes[1, 1].grid(True, alpha=0.3)

    fig.suptitle("Histogram Equalization: Transfer Function & CDF Analysis", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": filename}


def compute_multi_equalize(filenames_chapters):
    """Equalize multiple images and display comparison grid."""
    results = []
    for item in filenames_chapters[:4]:
        fn = item.get('filename', '')
        ch = item.get('chapter', 'CH02')
        img = load_image(fn, ch)
        if img is not None:
            eq = cv2.equalizeHist(img)
            results.append((fn, img, eq))

    if not results:
        return None

    n = len(results)
    fig, axes = plt.subplots(n, 2, figsize=(12, 5 * n))
    if n == 1:
        axes = axes.reshape(1, -1)

    for i, (fn, orig, eq) in enumerate(results):
        axes[i, 0].imshow(orig, cmap='gray', vmin=0, vmax=255)
        axes[i, 0].set_title(f"Original: {fn[:30]}...")
        axes[i, 0].axis('off')
        axes[i, 1].imshow(eq, cmap='gray', vmin=0, vmax=255)
        axes[i, 1].set_title("Equalized")
        axes[i, 1].axis('off')

    fig.suptitle("Histogram Equalization: Multi-Image Comparison", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "count": n}
