"""Practical 3: Image Negation, Grayscale Conversion, Subtraction, and Inversion."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


RECOMMENDED_PAIRS = [
    {
        "name": "Digital Subtraction Angiography",
        "image1": "Fig0228(a)(angiography_mask_image).tif",
        "image2": "Fig0228(b)(angiography_live_ image).tif",
    },
    {
        "name": "Dental X-ray Subtraction",
        "image1": "Fig0230(a)(dental_xray).tif",
        "image2": "Fig0230(b)(dental_xray_mask).tif",
    },
    {
        "name": "Shading Correction (Tungsten)",
        "image1": "Fig0229(a)(tungsten_filament_shaded).tif",
        "image2": "Fig0229(b)(tungsten_sensor_shading).tif",
    },
]


def compute_negation(filename):
    """Compute image negative: s = 255 - r. Returns original, negative, and histogram comparison."""
    img = load_image(filename)
    if img is None:
        return None

    negative = 255 - img

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    axes[0, 0].imshow(img, cmap='gray')
    axes[0, 0].set_title("Original Image")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(negative, cmap='gray')
    axes[0, 1].set_title("Negative (s = 255 - r)")
    axes[0, 1].axis('off')

    axes[1, 0].hist(img.ravel(), bins=256, range=(0, 256), color='black', alpha=0.7)
    axes[1, 0].set_title("Original Histogram")
    axes[1, 0].set_xlabel("Intensity")
    axes[1, 0].set_ylabel("Frequency")

    axes[1, 1].hist(negative.ravel(), bins=256, range=(0, 256), color='black', alpha=0.7)
    axes[1, 1].set_title("Negative Histogram")
    axes[1, 1].set_xlabel("Intensity")
    axes[1, 1].set_ylabel("Frequency")

    fig.suptitle(f"Image Negation: {filename}", fontsize=13, fontweight='bold')
    fig.tight_layout()

    return {
        "original": image_to_base64_png(img),
        "negative": image_to_base64_png(negative),
        "plot": fig_to_base64(fig),
        "filename": filename,
    }


def compute_subtraction(image1, image2):
    """Compute absolute difference |img1 - img2|. Returns both images + difference."""
    img1 = load_image(image1)
    img2 = load_image(image2)
    if img1 is None or img2 is None:
        return None

    # Resize to match if needed
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    difference = cv2.absdiff(img1, img2)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(img1, cmap='gray')
    axes[0].set_title("Image 1")
    axes[0].axis('off')

    axes[1].imshow(img2, cmap='gray')
    axes[1].set_title("Image 2")
    axes[1].axis('off')

    axes[2].imshow(difference, cmap='gray')
    axes[2].set_title("|Image1 - Image2|")
    axes[2].axis('off')

    fig.suptitle("Image Subtraction (Absolute Difference)", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "image1": image_to_base64_png(img1),
        "image2": image_to_base64_png(img2),
        "difference": image_to_base64_png(difference),
        "plot": fig_to_base64(fig),
        "stats": {
            "mean_diff": round(float(difference.mean()), 2),
            "max_diff": int(difference.max()),
            "nonzero_pct": round(float(np.count_nonzero(difference) / difference.size * 100), 2),
        }
    }


def compute_inversion(filename):
    """Compute intensity inversion (same as negation but named differently for clarity)."""
    return compute_negation(filename)


def compute_pipeline(image1, image2):
    """Full pipeline: subtraction → negation → enhancement. Returns 2x3 plot."""
    img1 = load_image(image1)
    img2 = load_image(image2)
    if img1 is None or img2 is None:
        return None

    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    difference = cv2.absdiff(img1, img2)
    neg_img1 = 255 - img1
    inverted_diff = 255 - difference
    enhanced = cv2.normalize(difference, None, 0, 255, cv2.NORM_MINMAX)

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    axes[0, 0].imshow(img1, cmap='gray')
    axes[0, 0].set_title("1. Image 1")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img2, cmap='gray')
    axes[0, 1].set_title("2. Image 2")
    axes[0, 1].axis('off')

    axes[0, 2].imshow(difference, cmap='gray')
    axes[0, 2].set_title("3. |Img1 - Img2|")
    axes[0, 2].axis('off')

    axes[1, 0].imshow(neg_img1, cmap='gray')
    axes[1, 0].set_title("4. Negation of Img1")
    axes[1, 0].axis('off')

    axes[1, 1].imshow(inverted_diff, cmap='gray')
    axes[1, 1].set_title("5. Inverted Difference")
    axes[1, 1].axis('off')

    axes[1, 2].imshow(enhanced, cmap='gray')
    axes[1, 2].set_title("6. Enhanced Result")
    axes[1, 2].axis('off')

    fig.suptitle("Complete Pipeline: Subtraction → Negation → Enhancement", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig)}
