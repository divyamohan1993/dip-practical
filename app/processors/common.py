"""
Shared image processing utilities for DIP Practical.
Provides image loading, encoding, and common helpers used across all practicals.
Auto-downloads the dataset if not present.
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
import zipfile
import urllib.request
import shutil
from pathlib import Path


IMAGES_DIR = Path(__file__).parent.parent.parent / "DIP3E_CH02_Original_Images" / "DIP3E_Original_Images_CH02"

# GitHub raw URL for the dataset (the repo itself contains these images)
DATASET_REPO_URL = "https://github.com/divyamohan1993/dip-practical/archive/refs/heads/main.zip"


def ensure_dataset():
    """Download the dataset if it doesn't exist locally."""
    if IMAGES_DIR.exists() and any(IMAGES_DIR.glob("*.tif")):
        return  # Dataset already present

    print("[DIP] Dataset not found. Downloading from GitHub...")
    zip_path = IMAGES_DIR.parent.parent / "_dataset_download.zip"
    extract_path = IMAGES_DIR.parent.parent / "_dataset_extract"

    try:
        # Download the repo zip
        urllib.request.urlretrieve(DATASET_REPO_URL, str(zip_path))
        print("[DIP] Download complete. Extracting images...")

        # Extract
        with zipfile.ZipFile(str(zip_path), 'r') as z:
            # Find the images inside the zip
            tif_files = [f for f in z.namelist() if f.endswith('.tif')]
            readme_files = [f for f in z.namelist() if '0_README' in f]

            if not tif_files:
                print("[DIP] ERROR: No .tif files found in downloaded archive.")
                return

            # Create target directory
            IMAGES_DIR.mkdir(parents=True, exist_ok=True)

            # Extract only the image files
            for fpath in tif_files + readme_files:
                fname = os.path.basename(fpath)
                if fname:
                    with z.open(fpath) as src, open(str(IMAGES_DIR / fname), 'wb') as dst:
                        dst.write(src.read())

        count = len(list(IMAGES_DIR.glob("*.tif")))
        print(f"[DIP] Dataset ready: {count} images in {IMAGES_DIR}")

    except Exception as e:
        print(f"[DIP] ERROR downloading dataset: {e}")
    finally:
        # Cleanup temp files
        if zip_path.exists():
            zip_path.unlink()
        if extract_path.exists():
            shutil.rmtree(str(extract_path), ignore_errors=True)


# Auto-download on import
ensure_dataset()


def get_available_images():
    """Return list of available images with metadata."""
    images = []
    if not IMAGES_DIR.exists():
        return images

    for f in sorted(IMAGES_DIR.iterdir()):
        if f.suffix.lower() == '.tif':
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                h, w = img.shape
                images.append({
                    "filename": f.name,
                    "width": w,
                    "height": h,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "display_name": _parse_image_name(f.name)
                })
    return images


def _parse_image_name(filename):
    """Extract a human-readable name from the filename."""
    name = filename.replace('.tif', '')
    # Extract figure number and description
    if '(' in name:
        parts = name.split('(', 1)
        fig_num = parts[0].strip()
        desc = parts[1].rstrip(')')
        # Clean up nested parentheses
        desc = desc.replace('(', ' - ').replace(')', '')
        return f"{fig_num}: {desc}"
    return name


def load_image(filename):
    """Load a TIF image as grayscale numpy array."""
    path = IMAGES_DIR / filename
    if not path.exists():
        return None
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return img


def image_to_base64_png(img):
    """Convert numpy array to base64-encoded PNG string."""
    if img is None:
        return None
    success, buffer = cv2.imencode('.png', img)
    if not success:
        return None
    return base64.b64encode(buffer).decode('utf-8')


def fig_to_base64(fig, dpi=120):
    """
    Render a matplotlib figure to a base64-encoded PNG string.

    Saves the figure, closes it to free memory, and returns the encoded bytes.
    Uses fig-scoped methods for thread safety (no plt globals).
    """
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
