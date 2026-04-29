"""Practical 8: Spatial Filtering (Box, Median, Laplacian, Sobel)."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


# Default images (Gonzalez & Woods Chapter 3 canonical figures)
DEFAULT_BOX_IMAGE = "Fig0333(a)(test_pattern_blurring_orig).tif"
DEFAULT_NOISY_IMAGE = "Fig0335(a)(ckt_board_saltpep_prob_pt05).tif"
DEFAULT_MOON_IMAGE = "Fig0338(a)(blurry_moon).tif"
DEFAULT_LENS_IMAGE = "Fig0342(a)(contact_lens_original).tif"

# CH03 fallback variants (G&W repackaged the dataset more than once,
# so filenames vary; if the default isn't present try these)
NOISY_VARIANTS = [
    "Fig0335(a)(ckt_board_saltpep_prob_pt05).tif",
    "Fig0335(a)(ckt_board_saltpr_5).tif",
    "Fig0335(a)(ckt_board_saltpep_5).tif",
]
MOON_VARIANTS = ["Fig0338(a)(blurry_moon).tif", "Fig0338(a)(moon).tif"]
LENS_VARIANTS = [
    "Fig0342(a)(contact_lens_original).tif",
    "Fig0342(a)(contact_lens).tif",
]


def _resolve(variants, chapter='CH03'):
    """Return the first filename in the list that loads successfully."""
    for fn in variants:
        if load_image(fn, chapter) is not None:
            return fn
    return variants[0]


def _to_uint8(a):
    a = a - a.min()
    return (255.0 * a / max(a.max(), 1e-9)).astype(np.uint8)


def compute_box_series(filename=None, chapter='CH03',
                       kernel_sizes=(3, 5, 9, 15, 35)):
    """Apply the box (mean) filter at multiple kernel sizes and show the
    progressive blurring."""
    if not filename:
        filename = DEFAULT_BOX_IMAGE
    img = load_image(filename, chapter)
    if img is None:
        return None

    n = len(kernel_sizes)
    cols = 3
    rows = (n + cols) // cols  # +1 cell for the original
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.ravel()

    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Original"); axes[0].axis('off')

    for i, k in enumerate(kernel_sizes, start=1):
        out = cv2.blur(img, (k, k))
        axes[i].imshow(out, cmap='gray', vmin=0, vmax=255)
        axes[i].set_title(f"Box {k}x{k}"); axes[i].axis('off')

    for j in range(n + 1, len(axes)):
        axes[j].axis('off')

    fig.suptitle("Box Filter: Effect of Kernel Size",
                 fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "filename": filename,
        "kernel_sizes": list(kernel_sizes),
    }


def compute_median_series(filename=None, chapter='CH03',
                          kernel_sizes=(3, 5, 7, 9)):
    """Apply the median filter at multiple kernel sizes to a noisy image."""
    if not filename:
        filename = _resolve(NOISY_VARIANTS, chapter)
    img = load_image(filename, chapter)
    if img is None:
        return None

    n = len(kernel_sizes)
    fig, axes = plt.subplots(1, n + 1, figsize=(4 * (n + 1), 5))

    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Noisy Original"); axes[0].axis('off')

    for i, k in enumerate(kernel_sizes, start=1):
        out = cv2.medianBlur(img, k)
        axes[i].imshow(out, cmap='gray', vmin=0, vmax=255)
        axes[i].set_title(f"Median {k}x{k}"); axes[i].axis('off')

    fig.suptitle("Median Filter: Removing Salt & Pepper Noise",
                 fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "filename": filename,
        "kernel_sizes": list(kernel_sizes),
    }


def compute_box_vs_median(filename=None, chapter='CH03', k=3):
    """Direct comparison: box filter vs median filter on the same noisy input.
    Demonstrates that median preserves edges while box blurs them."""
    if not filename:
        filename = _resolve(NOISY_VARIANTS, chapter)
    img = load_image(filename, chapter)
    if img is None:
        return None

    box_out = cv2.blur(img, (k, k))
    med_out = cv2.medianBlur(img, k)
    diff_box = np.abs(img.astype(int) - box_out.astype(int)).astype(np.uint8)
    diff_med = np.abs(img.astype(int) - med_out.astype(int)).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes[0, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Noisy input"); axes[0, 0].axis('off')
    axes[0, 1].imshow(box_out, cmap='gray', vmin=0, vmax=255)
    axes[0, 1].set_title(f"Box {k}x{k}"); axes[0, 1].axis('off')
    axes[0, 2].imshow(med_out, cmap='gray', vmin=0, vmax=255)
    axes[0, 2].set_title(f"Median {k}x{k}"); axes[0, 2].axis('off')

    axes[1, 0].axis('off')
    axes[1, 1].imshow(diff_box, cmap='hot')
    axes[1, 1].set_title("Removed by box (noise + edges)"); axes[1, 1].axis('off')
    axes[1, 2].imshow(diff_med, cmap='hot')
    axes[1, 2].set_title("Removed by median (mostly noise)"); axes[1, 2].axis('off')

    fig.suptitle("Box vs Median: Edge Preservation",
                 fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "filename": filename,
        "stats": {
            "removed_by_box": round(float(diff_box.mean()), 3),
            "removed_by_median": round(float(diff_med.mean()), 3),
        },
    }


def compute_laplacian(filename=None, chapter='CH03'):
    """Laplacian sharpening with 4-neighbour and 8-neighbour kernels."""
    if not filename:
        filename = _resolve(MOON_VARIANTS, chapter)
    img = load_image(filename, chapter)
    if img is None:
        return None

    lap4 = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float64)
    lap8 = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]], dtype=np.float64)

    resp4 = cv2.filter2D(img.astype(np.float64), ddepth=-1, kernel=lap4)
    resp8 = cv2.filter2D(img.astype(np.float64), ddepth=-1, kernel=lap8)

    sharp4 = np.clip(img.astype(np.float64) - resp4, 0, 255).astype(np.uint8)
    sharp8 = np.clip(img.astype(np.float64) - resp8, 0, 255).astype(np.uint8)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes[0, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Original"); axes[0, 0].axis('off')
    axes[0, 1].imshow(_to_uint8(resp4), cmap='gray')
    axes[0, 1].set_title("Laplacian (4-neighbour)"); axes[0, 1].axis('off')
    axes[0, 2].imshow(sharp4, cmap='gray', vmin=0, vmax=255)
    axes[0, 2].set_title("Sharpened: f - lap4"); axes[0, 2].axis('off')

    axes[1, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[1, 0].set_title("Original"); axes[1, 0].axis('off')
    axes[1, 1].imshow(_to_uint8(resp8), cmap='gray')
    axes[1, 1].set_title("Laplacian (8-neighbour)"); axes[1, 1].axis('off')
    axes[1, 2].imshow(sharp8, cmap='gray', vmin=0, vmax=255)
    axes[1, 2].set_title("Sharpened: f - lap8"); axes[1, 2].axis('off')

    fig.suptitle("Laplacian Sharpening", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": filename}


def compute_sobel(filename=None, chapter='CH03'):
    """Sobel edge detection: Gx, Gy, magnitude, direction, and threshold."""
    if not filename:
        filename = _resolve(LENS_VARIANTS, chapter)
    img = load_image(filename, chapter)
    if img is None:
        return None

    sx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    sy = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

    Gx = cv2.filter2D(img.astype(np.float64), ddepth=-1, kernel=sx)
    Gy = cv2.filter2D(img.astype(np.float64), ddepth=-1, kernel=sy)
    Gmag = np.abs(Gx) + np.abs(Gy)
    Gmag_disp = np.clip(255.0 * Gmag / max(Gmag.max(), 1e-9), 0, 255).astype(np.uint8)
    Gtheta = np.arctan2(Gy, Gx)
    th_disp = ((Gtheta + np.pi) / (2 * np.pi) * 255).astype(np.uint8)
    thresh = (Gmag_disp > 64).astype(np.uint8) * 255

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes[0, 0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0, 0].set_title("Original"); axes[0, 0].axis('off')
    axes[0, 1].imshow(_to_uint8(np.abs(Gx)), cmap='gray')
    axes[0, 1].set_title("|Gx| (vertical edges)"); axes[0, 1].axis('off')
    axes[0, 2].imshow(_to_uint8(np.abs(Gy)), cmap='gray')
    axes[0, 2].set_title("|Gy| (horizontal edges)"); axes[0, 2].axis('off')
    axes[1, 0].imshow(Gmag_disp, cmap='gray')
    axes[1, 0].set_title("|G| = |Gx|+|Gy|"); axes[1, 0].axis('off')
    axes[1, 1].imshow(th_disp, cmap='hsv')
    axes[1, 1].set_title("Gradient direction"); axes[1, 1].axis('off')
    axes[1, 2].imshow(thresh, cmap='gray', vmin=0, vmax=255)
    axes[1, 2].set_title("Thresholded edges"); axes[1, 2].axis('off')

    fig.suptitle("Sobel Edge Detection", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": filename}
