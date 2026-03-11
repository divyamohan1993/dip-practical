"""
Practical 2 -- Image Subtraction & Inversion (Gonzalez & Woods Ch. 2-3).

Performs image subtraction (absolute difference) and intensity inversion
(negation) on the first and last images of the Chapter 2 dataset.

All operations use NumPy arithmetic on grayscale uint8 arrays.
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
    get_available_images,
)


# ---------------------------------------------------------------------------
# Target images: first and last from the sorted dataset
# ---------------------------------------------------------------------------

def get_target_images():
    """
    Return the first and last image filenames from the dataset.

    Returns
    -------
    dict with keys: first, last (filenames), first_display, last_display.
    """
    images = get_available_images()
    if not images:
        return None
    first = images[0]
    last = images[-1]
    return {
        "first": first["filename"],
        "last": last["filename"],
        "first_display": first.get("display_name", first["filename"]),
        "last_display": last.get("display_name", last["filename"]),
        "first_meta": first,
        "last_meta": last,
    }


def _image_stats(img):
    """Return basic statistics for a uint8 image array."""
    return {
        "min": int(img.min()),
        "max": int(img.max()),
        "mean": round(float(img.mean()), 2),
        "std": round(float(img.std()), 2),
    }


# ---------------------------------------------------------------------------
# 1. Image Subtraction (Absolute Difference)
# ---------------------------------------------------------------------------

def compute_subtraction(filename1, filename2):
    """
    Compute the absolute difference |img1 - img2|.

    If images have different sizes, the smaller is resized to match the larger.

    Returns
    -------
    dict with keys: image1, image2, difference, enhanced, stats, resized.
    None if either image cannot be loaded.
    """
    img1 = load_image(filename1)
    img2 = load_image(filename2)
    if img1 is None or img2 is None:
        return None

    resized = False
    if img1.shape != img2.shape:
        resized = True
        # Resize to the larger dimensions
        h = max(img1.shape[0], img2.shape[0])
        w = max(img1.shape[1], img2.shape[1])
        import cv2
        img1 = cv2.resize(img1, (w, h), interpolation=cv2.INTER_LINEAR)
        img2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_LINEAR)

    # Absolute difference
    diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16)).astype(np.uint8)

    # Enhanced (contrast-stretched) difference for visibility
    d_min, d_max = int(diff.min()), int(diff.max())
    if d_max > d_min:
        enhanced = ((diff.astype(np.float64) - d_min) / (d_max - d_min) * 255).astype(np.uint8)
    else:
        enhanced = np.zeros_like(diff)

    return {
        "image1": image_to_base64_png(img1),
        "image2": image_to_base64_png(img2),
        "difference": image_to_base64_png(diff),
        "enhanced": image_to_base64_png(enhanced),
        "resized": resized,
        "stats": {
            "image1": _image_stats(img1),
            "image2": _image_stats(img2),
            "difference": _image_stats(diff),
        },
    }


def generate_subtraction_plot(filename1, filename2):
    """
    Generate a 2x4 comparison figure: originals, difference, histograms.

    Returns
    -------
    str: Base64-encoded PNG of the comparison plot.
    None if images cannot be loaded.
    """
    img1 = load_image(filename1)
    img2 = load_image(filename2)
    if img1 is None or img2 is None:
        return None

    if img1.shape != img2.shape:
        import cv2
        h = max(img1.shape[0], img2.shape[0])
        w = max(img1.shape[1], img2.shape[1])
        img1 = cv2.resize(img1, (w, h), interpolation=cv2.INTER_LINEAR)
        img2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_LINEAR)

    diff = np.abs(img1.astype(np.int16) - img2.astype(np.int16)).astype(np.uint8)
    d_min, d_max = int(diff.min()), int(diff.max())
    if d_max > d_min:
        enhanced = ((diff.astype(np.float64) - d_min) / (d_max - d_min) * 255).astype(np.uint8)
    else:
        enhanced = np.zeros_like(diff)

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle('Image Subtraction: |Image 1 - Image 2|', fontsize=14, fontweight='bold')

    # Row 1: Images
    axes[0, 0].imshow(img1, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title('Image 1 (First)', fontsize=10)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img2, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title('Image 2 (Last)', fontsize=10)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(diff, cmap='gray', vmin=0, vmax=255)
    axes[0, 2].set_title('|Difference|', fontsize=10)
    axes[0, 2].axis('off')

    axes[0, 3].imshow(enhanced, cmap='hot', vmin=0, vmax=255)
    axes[0, 3].set_title('Enhanced Difference', fontsize=10)
    axes[0, 3].axis('off')

    # Row 2: Histograms
    for idx, (img, title) in enumerate([
        (img1, 'Image 1 Histogram'),
        (img2, 'Image 2 Histogram'),
        (diff, 'Difference Histogram'),
    ]):
        axes[1, idx].hist(img.ravel(), bins=256, range=(0, 256),
                          color='#2c3e50', alpha=0.8, edgecolor='none')
        axes[1, idx].set_title(title, fontsize=10)
        axes[1, idx].set_xlim(0, 256)
        axes[1, idx].grid(True, alpha=0.3)

    # Overlaid histograms
    axes[1, 3].hist(img1.ravel(), bins=256, range=(0, 256),
                    color='#3498db', alpha=0.5, label='Image 1')
    axes[1, 3].hist(img2.ravel(), bins=256, range=(0, 256),
                    color='#e74c3c', alpha=0.5, label='Image 2')
    axes[1, 3].hist(diff.ravel(), bins=256, range=(0, 256),
                    color='#2ecc71', alpha=0.5, label='Difference')
    axes[1, 3].set_title('Overlaid Histograms', fontsize=10)
    axes[1, 3].set_xlim(0, 256)
    axes[1, 3].legend(fontsize=8)
    axes[1, 3].grid(True, alpha=0.3)

    fig.tight_layout()
    return fig_to_base64(fig, dpi=100)


# ---------------------------------------------------------------------------
# 2. Image Inversion (Negation)
# ---------------------------------------------------------------------------

def compute_inversion(filename):
    """
    Compute the intensity inversion s = 255 - r.

    Returns
    -------
    dict with keys: original, inverted, stats.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    inverted = (255 - img).astype(np.uint8)

    return {
        "original": image_to_base64_png(img),
        "inverted": image_to_base64_png(inverted),
        "stats": {
            "original": _image_stats(img),
            "inverted": _image_stats(inverted),
        },
    }


def generate_inversion_comparison(filename1, filename2):
    """
    Generate a 2x2 figure showing both images and their inversions.

    Returns
    -------
    str: Base64-encoded PNG.
    None if images cannot be loaded.
    """
    img1 = load_image(filename1)
    img2 = load_image(filename2)
    if img1 is None or img2 is None:
        return None

    inv1 = (255 - img1).astype(np.uint8)
    inv2 = (255 - img2).astype(np.uint8)

    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    fig.suptitle('Image Inversion: s = 255 - r', fontsize=14, fontweight='bold')

    axes[0, 0].imshow(img1, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title('Image 1: Original', fontsize=11)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(inv1, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title('Image 1: Inverted', fontsize=11)
    axes[0, 1].axis('off')

    axes[1, 0].imshow(img2, cmap='gray', vmin=0, vmax=255)
    axes[1, 0].set_title('Image 2: Original', fontsize=11)
    axes[1, 0].axis('off')

    axes[1, 1].imshow(inv2, cmap='gray', vmin=0, vmax=255)
    axes[1, 1].set_title('Image 2: Inverted', fontsize=11)
    axes[1, 1].axis('off')

    fig.tight_layout()
    return fig_to_base64(fig, dpi=100)


def generate_inversion_histograms(filename):
    """
    Generate a figure with original and inverted histograms side by side.

    Returns
    -------
    str: Base64-encoded PNG.
    None if the image cannot be loaded.
    """
    img = load_image(filename)
    if img is None:
        return None

    inverted = (255 - img).astype(np.uint8)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    fig.suptitle('Histogram: Original vs. Inverted', fontsize=13, fontweight='bold')

    axes[0].hist(img.ravel(), bins=256, range=(0, 256),
                 color='#2c3e50', alpha=0.8, edgecolor='none')
    axes[0].set_title('Original', fontsize=10)
    axes[0].set_xlim(0, 256)
    axes[0].set_xlabel('Intensity')
    axes[0].set_ylabel('Frequency')
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(inverted.ravel(), bins=256, range=(0, 256),
                 color='#c0392b', alpha=0.8, edgecolor='none')
    axes[1].set_title('Inverted (s = 255 - r)', fontsize=10)
    axes[1].set_xlim(0, 256)
    axes[1].set_xlabel('Intensity')
    axes[1].set_ylabel('Frequency')
    axes[1].grid(True, alpha=0.3)

    fig.tight_layout()
    return fig_to_base64(fig, dpi=100)


# ---------------------------------------------------------------------------
# 3. Combined: Subtraction of Inverted Images
# ---------------------------------------------------------------------------

def compute_combined_operations(filename1, filename2):
    """
    Demonstrate combined operations:
    1. Invert both images
    2. Subtract inverted images
    3. Compare with subtraction of originals

    Returns
    -------
    dict with results of combined operations.
    None if images cannot be loaded.
    """
    img1 = load_image(filename1)
    img2 = load_image(filename2)
    if img1 is None or img2 is None:
        return None

    if img1.shape != img2.shape:
        import cv2
        h = max(img1.shape[0], img2.shape[0])
        w = max(img1.shape[1], img2.shape[1])
        img1 = cv2.resize(img1, (w, h), interpolation=cv2.INTER_LINEAR)
        img2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_LINEAR)

    inv1 = (255 - img1).astype(np.uint8)
    inv2 = (255 - img2).astype(np.uint8)

    # Subtraction of originals
    diff_orig = np.abs(img1.astype(np.int16) - img2.astype(np.int16)).astype(np.uint8)

    # Subtraction of inverted
    diff_inv = np.abs(inv1.astype(np.int16) - inv2.astype(np.int16)).astype(np.uint8)

    # The absolute differences should be identical mathematically:
    # |inv1 - inv2| = |(255 - img1) - (255 - img2)| = |img2 - img1| = |img1 - img2|
    pixel_match = bool(np.array_equal(diff_orig, diff_inv))

    # Build the comparison figure
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    fig.suptitle('Combined Operations: Subtraction of Inverted Images',
                 fontsize=14, fontweight='bold')

    axes[0, 0].imshow(img1, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title('Original Image 1', fontsize=10)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img2, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title('Original Image 2', fontsize=10)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(diff_orig, cmap='gray', vmin=0, vmax=255)
    axes[0, 2].set_title('|Original 1 - Original 2|', fontsize=10)
    axes[0, 2].axis('off')

    axes[1, 0].imshow(inv1, cmap='gray', vmin=0, vmax=255)
    axes[1, 0].set_title('Inverted Image 1', fontsize=10)
    axes[1, 0].axis('off')

    axes[1, 1].imshow(inv2, cmap='gray', vmin=0, vmax=255)
    axes[1, 1].set_title('Inverted Image 2', fontsize=10)
    axes[1, 1].axis('off')

    axes[1, 2].imshow(diff_inv, cmap='gray', vmin=0, vmax=255)
    axes[1, 2].set_title('|Inverted 1 - Inverted 2|', fontsize=10)
    axes[1, 2].axis('off')

    fig.tight_layout()
    plot_b64 = fig_to_base64(fig, dpi=100)

    return {
        "inverted1": image_to_base64_png(inv1),
        "inverted2": image_to_base64_png(inv2),
        "diff_original": image_to_base64_png(diff_orig),
        "diff_inverted": image_to_base64_png(diff_inv),
        "plot": plot_b64,
        "pixel_match": pixel_match,
        "stats": {
            "diff_original": _image_stats(diff_orig),
            "diff_inverted": _image_stats(diff_inv),
        },
    }
