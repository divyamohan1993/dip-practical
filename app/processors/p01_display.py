"""Practical 1: Load and Display Image."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


def display_image(filename):
    """Load and return image with properties."""
    img = load_image(filename)
    if img is None:
        return None
    h, w = img.shape
    return {
        "image": image_to_base64_png(img),
        "filename": filename,
        "properties": {
            "height": h,
            "width": w,
            "dtype": str(img.dtype),
            "min": int(img.min()),
            "max": int(img.max()),
            "mean": round(float(img.mean()), 2),
            "std": round(float(img.std()), 2),
            "total_pixels": int(img.size),
        }
    }


def display_histogram(filename):
    """Generate histogram plot for an image."""
    img = load_image(filename)
    if img is None:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.imshow(img, cmap='gray')
    ax1.set_title(filename, fontsize=10)
    ax1.axis('off')

    ax2.hist(img.ravel(), bins=256, range=(0, 256), color='black', alpha=0.7)
    ax2.set_title("Pixel Intensity Histogram")
    ax2.set_xlabel("Intensity Value (0-255)")
    ax2.set_ylabel("Frequency")
    ax2.set_xlim(0, 256)

    fig.tight_layout()
    return {"plot": fig_to_base64(fig)}


def display_multiple(filenames):
    """Display up to 4 images in a 2x2 grid."""
    filenames = filenames[:4]
    n = len(filenames)
    if n == 0:
        return None

    rows = 2 if n > 2 else 1
    cols = 2 if n > 1 else 1
    fig, axes = plt.subplots(rows, cols, figsize=(10, 10 if rows == 2 else 5))
    if n == 1:
        axes = [axes]
    else:
        axes = axes.flatten()

    images_data = []
    for i, (ax, fname) in enumerate(zip(axes, filenames)):
        img = load_image(fname)
        if img is not None:
            ax.imshow(img, cmap='gray')
            h, w = img.shape
            ax.set_title(f"{fname.split('(')[-1].replace(').tif','')}\n{w}x{h}", fontsize=9)
            images_data.append({"filename": fname, "width": w, "height": h})
        ax.axis('off')

    # Hide unused axes
    for j in range(n, len(axes)):
        axes[j].axis('off')

    fig.suptitle("Multiple Images from Dataset", fontsize=14, fontweight='bold')
    fig.tight_layout()
    return {"plot": fig_to_base64(fig), "images": images_data}
