"""
Pre-compute all default practical outputs and save as static JSON cache.
Run this once at deploy time: python precompute.py
Results are served as static files — zero server computation at runtime.
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app.processors.common import get_available_images
from app.processors import p01_display, p02_downsampling, p03_negation_subtraction, p04_gamma

CACHE_DIR = os.path.join(os.path.dirname(__file__), "app", "static", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def save(name, data):
    path = os.path.join(CACHE_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f)
    size_kb = os.path.getsize(path) / 1024
    print(f"  {name}.json ({size_kb:.0f} KB)")


def main():
    images = get_available_images()
    if not images:
        print("ERROR: No images found. Ensure dataset is present.")
        return

    # Default images
    cameraman = next((i["filename"] for i in images if "cameraman" in i["filename"]), images[0]["filename"])
    body_scan = next((i["filename"] for i in images if "partial_body" in i["filename"]), images[0]["filename"])
    einstein_low = next((i["filename"] for i in images if "einstein low" in i["filename"]), images[0]["filename"])
    angio_mask = next((i["filename"] for i in images if "angiography_mask" in i["filename"]), None)
    angio_live = next((i["filename"] for i in images if "angiography_live" in i["filename"]), None)
    skull = next((i["filename"] for i in images if "ctskull" in i["filename"]), images[1]["filename"])
    galaxy = next((i["filename"] for i in images if "galaxy" in i["filename"]), images[2]["filename"])
    dental = next((i["filename"] for i in images if "dental_xray).tif" in i["filename"]), images[3]["filename"])

    print(f"Dataset: {len(images)} images")
    print(f"Defaults: {cameraman}, {body_scan}, {einstein_low}")
    print()

    # === Practical 1 ===
    print("Practical 1: Display")
    save("p1_display", p01_display.display_image(cameraman))
    save("p1_histogram", p01_display.display_histogram(cameraman))
    save("p1_multi", p01_display.display_multiple([cameraman, skull, dental, galaxy]))

    # === Practical 2 ===
    print("Practical 2: Downsampling")
    save("p2_downsample", p02_downsampling.downsample_series(cameraman, steps=5))
    save("p2_comparison", p02_downsampling.downsample_comparison_plot(cameraman))
    save("p2_upscale", p02_downsampling.upscale_comparison_plot(cameraman))

    # === Practical 3 ===
    print("Practical 3: Negation/Subtraction")
    save("p3_negate", p03_negation_subtraction.compute_negation(body_scan))
    if angio_mask and angio_live:
        save("p3_subtract", p03_negation_subtraction.compute_subtraction(angio_mask, angio_live))
        save("p3_pipeline", p03_negation_subtraction.compute_pipeline(angio_mask, angio_live))

    # === Practical 4 ===
    print("Practical 4: Gamma")
    save("p4_gamma", p04_gamma.apply_gamma(einstein_low, gamma=0.4))
    save("p4_series", p04_gamma.gamma_series(einstein_low))
    save("p4_curves", p04_gamma.transformation_curves())
    save("p4_log", p04_gamma.log_transform(einstein_low))
    save("p4_contrast", p04_gamma.contrast_enhancement(einstein_low, mode="dark"))

    # === Image list ===
    save("images", {"images": images, "count": len(images)})

    print(f"\nDone! {len(os.listdir(CACHE_DIR))} cache files in {CACHE_DIR}")


if __name__ == "__main__":
    main()
