"""
API routes for DIP Practical web application.
All endpoints are registered under the /api prefix via the blueprint.

Provides both namespaced URLs (e.g. /api/p1/spatial-difference) and
backward-compatible flat URLs (e.g. /api/spatial-difference) that
redirect to the new paths.
"""

from flask import Blueprint, jsonify, request, redirect, url_for

from app.processors.common import (
    get_available_images,
    load_image,
    image_to_base64_png,
)
from app.processors.p01_spatial_diff import (
    RECOMMENDED_PAIRS,
    MATPLOTLIB_REFERENCE,
    compute_spatial_difference,
    generate_histogram,
    generate_comparison_plot,
    generate_matplotlib_demo,
    get_pixel_region,
    get_step_by_step_pipeline,
    generate_surface_plot,
    compute_pixel_arithmetic,
    generate_bit_depth_comparison,
)

api_bp = Blueprint('api', __name__)


# -----------------------------------------------------------------------
# Shared endpoints (not practical-specific)
# -----------------------------------------------------------------------

@api_bp.route('/images')
def api_images():
    """List all available images with metadata."""
    images = get_available_images()
    return jsonify({
        "images": images,
        "count": len(images),
        "recommended_pairs": RECOMMENDED_PAIRS
    })


@api_bp.route('/image/<path:filename>')
def api_image(filename):
    """Serve a specific image as base64 PNG."""
    img = load_image(filename)
    if img is None:
        return jsonify({"error": f"Image not found: {filename}"}), 404
    b64 = image_to_base64_png(img)
    return jsonify({"image": b64, "filename": filename})


# -----------------------------------------------------------------------
# Practical 1 — Namespaced endpoints (/api/p1/...)
# -----------------------------------------------------------------------

@api_bp.route('/p1/spatial-difference', methods=['POST'])
def p1_spatial_difference():
    """Compute spatial difference between two images."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400

    result = compute_spatial_difference(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to process images. Check filenames."}), 400

    return jsonify(result)


@api_bp.route('/p1/histogram', methods=['POST'])
def p1_histogram():
    """Generate histogram for an image."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400

    result = generate_histogram(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate histogram"}), 400

    return jsonify({"histogram": result})


@api_bp.route('/p1/comparison-plot', methods=['POST'])
def p1_comparison_plot():
    """Generate a full comparison plot."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400

    result = generate_comparison_plot(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to generate comparison plot"}), 400

    return jsonify({"plot": result})


@api_bp.route('/p1/matplotlib-reference')
def p1_matplotlib_reference():
    """Return comprehensive matplotlib reference."""
    return jsonify(MATPLOTLIB_REFERENCE)


@api_bp.route('/p1/matplotlib-demos')
def p1_matplotlib_demos():
    """Generate and return matplotlib demonstration plots."""
    demos = generate_matplotlib_demo()
    return jsonify({"demos": demos})


@api_bp.route('/p1/pixel-view', methods=['POST'])
def p1_pixel_view():
    """Return raw pixel values for a square region around (x, y)."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400

    x = int(data.get('x', 0))
    y = int(data.get('y', 0))
    size = int(data.get('size', 10))

    result = get_pixel_region(data['filename'], x, y, size)
    if result is None:
        return jsonify({"error": "Failed to load image. Check filename."}), 400

    return jsonify(result)


@api_bp.route('/p1/step-by-step', methods=['POST'])
def p1_step_by_step():
    """Return a comprehensive step-by-step breakdown of the spatial
    difference pipeline between two images."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400

    result = get_step_by_step_pipeline(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to process images. Check filenames."}), 400

    return jsonify(result)


@api_bp.route('/p1/surface-plot', methods=['POST'])
def p1_surface_plot():
    """Generate a 3-D surface plot of pixel intensities for a region."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400

    x = int(data.get('x', 0))
    y = int(data.get('y', 0))
    size = int(data.get('size', 64))

    result = generate_surface_plot(data['filename'], region_x=x, region_y=y,
                                   region_size=size)
    if result is None:
        return jsonify({"error": "Failed to generate surface plot."}), 400

    return jsonify({"plot": result})


@api_bp.route('/p1/pixel-arithmetic', methods=['POST'])
def p1_pixel_arithmetic():
    """Demonstrate uint8 arithmetic on two pixel values (0-255)."""
    data = request.get_json()
    if not data or 'val1' not in data or 'val2' not in data:
        return jsonify({"error": "Provide 'val1' and 'val2' (integers 0-255)"}), 400

    try:
        val1 = int(data['val1'])
        val2 = int(data['val2'])
    except (ValueError, TypeError):
        return jsonify({"error": "val1 and val2 must be integers"}), 400

    if not (0 <= val1 <= 255 and 0 <= val2 <= 255):
        return jsonify({"error": "val1 and val2 must be in range 0-255"}), 400

    result = compute_pixel_arithmetic(val1, val2)
    return jsonify(result)


@api_bp.route('/p1/bit-depth', methods=['POST'])
def p1_bit_depth():
    """Return base64 PNGs showing the same image at 8, 4, 2, and 1-bit
    depth with corresponding histograms."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400

    result = generate_bit_depth_comparison(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate bit-depth comparison."}), 400

    return jsonify({"images": result})


# -----------------------------------------------------------------------
# Backward-compatible flat endpoints (/api/...)
# These aliases call the same handler functions directly so that
# existing frontend code and bookmarks continue to work.
# -----------------------------------------------------------------------

@api_bp.route('/spatial-difference', methods=['POST'])
def api_spatial_difference():
    """Backward compat: /api/spatial-difference -> same as /api/p1/spatial-difference."""
    return p1_spatial_difference()


@api_bp.route('/histogram', methods=['POST'])
def api_histogram():
    """Backward compat: /api/histogram -> same as /api/p1/histogram."""
    return p1_histogram()


@api_bp.route('/comparison-plot', methods=['POST'])
def api_comparison_plot():
    """Backward compat: /api/comparison-plot -> same as /api/p1/comparison-plot."""
    return p1_comparison_plot()


@api_bp.route('/matplotlib-reference')
def api_matplotlib_reference():
    """Backward compat: /api/matplotlib-reference -> same as /api/p1/matplotlib-reference."""
    return p1_matplotlib_reference()


@api_bp.route('/matplotlib-demos')
def api_matplotlib_demos():
    """Backward compat: /api/matplotlib-demos -> same as /api/p1/matplotlib-demos."""
    return p1_matplotlib_demos()


@api_bp.route('/pixel-view', methods=['POST'])
def api_pixel_view():
    """Backward compat: /api/pixel-view -> same as /api/p1/pixel-view."""
    return p1_pixel_view()


@api_bp.route('/step-by-step', methods=['POST'])
def api_step_by_step():
    """Backward compat: /api/step-by-step -> same as /api/p1/step-by-step."""
    return p1_step_by_step()


@api_bp.route('/surface-plot', methods=['POST'])
def api_surface_plot():
    """Backward compat: /api/surface-plot -> same as /api/p1/surface-plot."""
    return p1_surface_plot()


@api_bp.route('/pixel-arithmetic', methods=['POST'])
def api_pixel_arithmetic():
    """Backward compat: /api/pixel-arithmetic -> same as /api/p1/pixel-arithmetic."""
    return p1_pixel_arithmetic()


@api_bp.route('/bit-depth', methods=['POST'])
def api_bit_depth():
    """Backward compat: /api/bit-depth -> same as /api/p1/bit-depth."""
    return p1_bit_depth()


# -----------------------------------------------------------------------
# Practical 2 — Image Subtraction & Inversion (/api/p2/...)
# Lazy imports: processor loaded on first request, not at startup.
# -----------------------------------------------------------------------

def _p2():
    """Lazy-load the P2 processor module."""
    from app.processors import p02_subtraction_inversion
    return p02_subtraction_inversion


@api_bp.route('/p2/targets')
def p2_targets():
    """Return the first and last image filenames from the dataset."""
    result = _p2().get_target_images()
    if result is None:
        return jsonify({"error": "No images found in dataset"}), 400
    return jsonify(result)


@api_bp.route('/p2/subtract', methods=['POST'])
def p2_subtract():
    """Compute absolute difference between two images."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400
    result = _p2().compute_subtraction(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to process images"}), 400
    return jsonify(result)


@api_bp.route('/p2/subtract-plot', methods=['POST'])
def p2_subtract_plot():
    """Generate a full subtraction comparison plot."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400
    result = _p2().generate_subtraction_plot(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to generate plot"}), 400
    return jsonify({"plot": result})


@api_bp.route('/p2/invert', methods=['POST'])
def p2_invert():
    """Compute intensity inversion (negation) of an image."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p2().compute_inversion(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to process image"}), 400
    return jsonify(result)


@api_bp.route('/p2/invert-histogram', methods=['POST'])
def p2_invert_histogram():
    """Generate histogram comparison for original vs. inverted image."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p2().generate_inversion_histograms(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate histograms"}), 400
    return jsonify({"plot": result})


@api_bp.route('/p2/invert-comparison', methods=['POST'])
def p2_invert_comparison():
    """Generate side-by-side inversion comparison for two images."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400
    result = _p2().generate_inversion_comparison(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to generate comparison"}), 400
    return jsonify({"plot": result})


@api_bp.route('/p2/combined', methods=['POST'])
def p2_combined():
    """Run combined subtraction + inversion operations."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400
    result = _p2().compute_combined_operations(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to process images"}), 400
    return jsonify(result)


# -----------------------------------------------------------------------
# Practical 3 — Histogram Equalization & CLAHE (/api/p3/...)
# Lazy imports: processor loaded on first request, not at startup.
# -----------------------------------------------------------------------

def _p3():
    """Lazy-load the P3 processor module."""
    from app.processors import p03_histogram
    return p03_histogram


@api_bp.route('/p3/equalize', methods=['POST'])
def p3_equalize():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p3().compute_histogram_equalization(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to equalize histogram"}), 400
    return jsonify(result)


@api_bp.route('/p3/clahe', methods=['POST'])
def p3_clahe():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p3().compute_clahe(data['filename'],
                                 clip_limit=float(data.get('clip_limit', 2.0)),
                                 tile_size=int(data.get('tile_size', 8)))
    if result is None:
        return jsonify({"error": "Failed to apply CLAHE"}), 400
    return jsonify(result)


@api_bp.route('/p3/match', methods=['POST'])
def p3_match():
    data = request.get_json()
    if not data or 'source' not in data or 'target' not in data:
        return jsonify({"error": "Provide 'source' and 'target' filenames"}), 400
    result = _p3().compute_histogram_matching(data['source'], data['target'])
    if result is None:
        return jsonify({"error": "Failed to match histograms"}), 400
    return jsonify(result)


@api_bp.route('/p3/local-stats', methods=['POST'])
def p3_local_stats():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p3().compute_local_histogram_stats(data['filename'],
                                                  window_size=int(data.get('window_size', 3)))
    if result is None:
        return jsonify({"error": "Failed to compute local stats"}), 400
    return jsonify(result)


@api_bp.route('/p3/walkthrough', methods=['POST'])
def p3_walkthrough():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p3().generate_histogram_walkthrough(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate walkthrough"}), 400
    return jsonify(result)


@api_bp.route('/p3/histogram-data', methods=['POST'])
def p3_histogram_data():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p3().get_histogram_data(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to get histogram data"}), 400
    return jsonify(result)
