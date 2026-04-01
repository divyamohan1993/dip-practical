#!/usr/bin/env python3
"""
DIP Practical — Dataset Setup (run once)
Downloads the Gonzalez & Woods CH02 dataset and converts TIF images to PNG.
Result: data/CH02/*.png files ready for static serving.

Usage: python setup.py
Requires: pip install Pillow
"""

import json
import os
import urllib.request
import zipfile
from PIL import Image

CHAPTER = "CH02"
DOWNLOAD_BASE = "https://www.imageprocessingplace.com/downloads_V3/dip3e_downloads/dip3e_book_images"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data", CHAPTER)
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "data", "manifest.json")


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Check if already populated
    existing = [f for f in os.listdir(DATA_DIR) if f.endswith(".png")]
    if existing:
        print(f"Already have {len(existing)} PNG images in data/{CHAPTER}/")
        print("Delete the folder to re-download.")
        return

    # Download
    zip_name = f"DIP3E_{CHAPTER}_Original_Images.zip"
    url = f"{DOWNLOAD_BASE}/{zip_name}"
    zip_path = os.path.join(SCRIPT_DIR, "_tmp_download.zip")

    print(f"Downloading {CHAPTER} dataset from imageprocessingplace.com...")
    urllib.request.urlretrieve(url, zip_path)

    # Extract TIF and convert to PNG
    images = []
    with zipfile.ZipFile(zip_path, "r") as z:
        tif_files = [f for f in z.namelist() if f.lower().endswith(".tif")]
        print(f"Converting {len(tif_files)} TIF images to PNG...")
        for fpath in tif_files:
            fname = os.path.basename(fpath)
            if not fname:
                continue

            # Extract TIF to temp
            tif_data = z.read(fpath)
            tif_tmp = os.path.join(DATA_DIR, fname)
            with open(tif_tmp, "wb") as f:
                f.write(tif_data)

            # Convert to PNG
            png_name = fname.replace(".tif", ".png").replace(".TIF", ".png")
            png_path = os.path.join(DATA_DIR, png_name)

            img = Image.open(tif_tmp)
            img.save(png_path, "PNG")
            w, h = img.size
            size_kb = round(os.path.getsize(png_path) / 1024, 1)

            # Build display name
            name = fname.replace(".tif", "").replace(".TIF", "")
            if "(" in name:
                parts = name.split("(", 1)
                fig_num = parts[0].strip()
                desc = parts[1].rstrip(")").replace("(", " - ").replace(")", "")
                display_name = f"{fig_num}: {desc}"
            else:
                display_name = name

            images.append({
                "filename": png_name,
                "display_name": display_name,
                "width": w,
                "height": h,
                "size_kb": size_kb,
            })

            # Remove TIF
            os.remove(tif_tmp)
            print(f"  {png_name} ({w}x{h}, {size_kb} KB)")

    # Cleanup
    os.remove(zip_path)

    # Sort and save manifest
    images.sort(key=lambda x: x["filename"])
    manifest = {
        "chapter": CHAPTER,
        "chapter_name": "Digital Image Fundamentals",
        "image_count": len(images),
        "images": images,
    }

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nDone! {len(images)} PNG images in data/{CHAPTER}/")
    print(f"Manifest: data/manifest.json")


if __name__ == "__main__":
    main()
