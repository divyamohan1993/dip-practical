"""
Shared image processing utilities for DIP Practical.
Multi-chapter dataset support with on-demand download from public source.
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
from pathlib import Path
import threading


DATASETS_DIR = Path(__file__).parent.parent.parent / "datasets"

DOWNLOAD_BASE = "https://www.imageprocessingplace.com/downloads_V3/dip3e_downloads/dip3e_book_images"

CHAPTERS = [
    {"id": "CH01", "num": 1, "name": "Introduction", "zip": "DIP3E_CH01_Original_Images.zip", "size": "19.1 MB"},
    {"id": "CH02", "num": 2, "name": "Digital Image Fundamentals", "zip": "DIP3E_CH02_Original_Images.zip", "size": "8.2 MB"},
    {"id": "CH03", "num": 3, "name": "Intensity Transformations & Spatial Filtering", "zip": "DIP3E_CH03_Original_Images.zip", "size": "3.8 MB"},
    {"id": "CH04", "num": 4, "name": "Filtering in the Frequency Domain", "zip": "DIP3E_CH04_Original_Images.zip", "size": "4.2 MB"},
    {"id": "CH05", "num": 5, "name": "Image Restoration & Reconstruction", "zip": "DIP3E_CH05_Original_Images.zip", "size": "4.9 MB"},
    {"id": "CH06", "num": 6, "name": "Color Image Processing", "zip": "DIP3E_CH06_Original_Images.zip", "size": "22.4 MB"},
    {"id": "CH07", "num": 7, "name": "Wavelets & Multiresolution Processing", "zip": "DIP3E_CH07_Original_Images.zip", "size": "740 KB"},
    {"id": "CH08", "num": 8, "name": "Image Compression", "zip": "DIP3E_CH08_Original_Images.zip", "size": "8.1 MB"},
    {"id": "CH09", "num": 9, "name": "Morphological Image Processing", "zip": "DIP3E_CH09_Original_Images.zip", "size": "2.3 MB"},
    {"id": "CH10", "num": 10, "name": "Image Segmentation", "zip": "DIP3E_CH10_Original_Images.zip", "size": "7.3 MB"},
    {"id": "CH11", "num": 11, "name": "Representation & Description", "zip": "DIP3E_CH11_Original_Images.zip", "size": "3.5 MB"},
    {"id": "CH12", "num": 12, "name": "Object Recognition", "zip": "DIP3E_CH12_Original_Images.zip", "size": "1.9 MB"},
]

_download_locks = {}
_lock_guard = threading.Lock()


def _get_lock(chapter_id):
    """Get or create a per-chapter download lock."""
    with _lock_guard:
        if chapter_id not in _download_locks:
            _download_locks[chapter_id] = threading.Lock()
        return _download_locks[chapter_id]


def get_chapter_dir(chapter_id):
    """Return the local directory for a chapter's images."""
    return DATASETS_DIR / chapter_id


def ensure_chapter(chapter_id):
    """Download a chapter's dataset if not already present. Thread-safe."""
    ch_dir = get_chapter_dir(chapter_id)
    if ch_dir.exists() and any(ch_dir.glob("*.tif")):
        return True

    chapter = next((c for c in CHAPTERS if c["id"] == chapter_id), None)
    if not chapter:
        return False

    lock = _get_lock(chapter_id)
    if not lock.acquire(timeout=300):
        return False

    try:
        # Re-check after acquiring lock (another thread may have downloaded)
        if ch_dir.exists() and any(ch_dir.glob("*.tif")):
            return True

        url = f"{DOWNLOAD_BASE}/{chapter['zip']}"
        zip_path = DATASETS_DIR / f"_tmp_{chapter_id}.zip"

        print(f"[DIP] Downloading {chapter_id}: {chapter['name']} ({chapter['size']})...")
        DATASETS_DIR.mkdir(parents=True, exist_ok=True)

        urllib.request.urlretrieve(url, str(zip_path))

        ch_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(str(zip_path), 'r') as z:
            tif_files = [f for f in z.namelist() if f.lower().endswith('.tif')]
            for fpath in tif_files:
                fname = os.path.basename(fpath)
                if fname:
                    with z.open(fpath) as src, open(str(ch_dir / fname), 'wb') as dst:
                        dst.write(src.read())

        count = len(list(ch_dir.glob("*.tif")))
        print(f"[DIP] {chapter_id} ready: {count} images")
        return count > 0

    except Exception as e:
        print(f"[DIP] ERROR downloading {chapter_id}: {e}")
        return False
    finally:
        if zip_path.exists():
            zip_path.unlink()
        lock.release()


def get_chapters():
    """Return list of chapters with download status."""
    result = []
    for ch in CHAPTERS:
        ch_dir = get_chapter_dir(ch["id"])
        downloaded = ch_dir.exists() and any(ch_dir.glob("*.tif"))
        count = len(list(ch_dir.glob("*.tif"))) if downloaded else 0
        result.append({
            "id": ch["id"],
            "num": ch["num"],
            "name": ch["name"],
            "size": ch["size"],
            "downloaded": downloaded,
            "image_count": count,
        })
    return result


def get_chapter_images(chapter_id):
    """Return images for a chapter. Downloads on first access."""
    if not ensure_chapter(chapter_id):
        return []

    ch_dir = get_chapter_dir(chapter_id)
    images = []
    for f in sorted(ch_dir.iterdir()):
        if f.suffix.lower() == '.tif':
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                h, w = img.shape
                images.append({
                    "filename": f.name,
                    "chapter": chapter_id,
                    "width": w,
                    "height": h,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "display_name": _parse_image_name(f.name),
                })
    return images


def get_available_images(chapter='CH02'):
    """Legacy wrapper — returns images for a single chapter."""
    return get_chapter_images(chapter)


def _parse_image_name(filename):
    """Extract a human-readable name from the filename."""
    name = filename.replace('.tif', '')
    if '(' in name:
        parts = name.split('(', 1)
        fig_num = parts[0].strip()
        desc = parts[1].rstrip(')')
        desc = desc.replace('(', ' - ').replace(')', '')
        return f"{fig_num}: {desc}"
    return name


def load_image(filename, chapter='CH02'):
    """Load a TIF image as grayscale numpy array from the given chapter."""
    ch_dir = get_chapter_dir(chapter)
    path = ch_dir / filename
    if not path.exists():
        if not ensure_chapter(chapter):
            return None
        path = ch_dir / filename
        if not path.exists():
            return None
    return cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)


def image_to_base64_png(img):
    """Convert numpy array to base64-encoded PNG string."""
    if img is None:
        return None
    success, buffer = cv2.imencode('.png', img)
    if not success:
        return None
    return base64.b64encode(buffer).decode('utf-8')


def fig_to_base64(fig, dpi=120):
    """Render a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')
