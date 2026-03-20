"""
API routes for DIP Practical web application.
All endpoints are registered under the /api prefix via the blueprint.
"""

from flask import Blueprint, jsonify, request

from app.processors.common import get_available_images, load_image, image_to_base64_png

api_bp = Blueprint('api', __name__)


# -----------------------------------------------------------------------
# Shared endpoints
# -----------------------------------------------------------------------

@api_bp.route('/images')
def api_images():
    """List all available images with metadata."""
    images = get_available_images()
    return jsonify({"images": images, "count": len(images)})


@api_bp.route('/image/<path:filename>')
def api_image(filename):
    """Serve a specific image as base64 PNG."""
    img = load_image(filename)
    if img is None:
        return jsonify({"error": f"Image not found: {filename}"}), 404
    b64 = image_to_base64_png(img)
    return jsonify({"image": b64, "filename": filename})


# -----------------------------------------------------------------------
# Practical 1 — Load & Display (/api/p1/...)
# -----------------------------------------------------------------------

def _p1():
    from app.processors import p01_display
    return p01_display


@api_bp.route('/p1/display', methods=['POST'])
def p1_display():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p1().display_image(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to load image"}), 400
    return jsonify(result)


@api_bp.route('/p1/histogram', methods=['POST'])
def p1_histogram():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p1().display_histogram(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate histogram"}), 400
    return jsonify(result)


@api_bp.route('/p1/multi-display', methods=['POST'])
def p1_multi_display():
    data = request.get_json()
    if not data or 'filenames' not in data:
        return jsonify({"error": "Provide 'filenames' array"}), 400
    result = _p1().display_multiple(data['filenames'])
    if result is None:
        return jsonify({"error": "Failed to display images"}), 400
    return jsonify(result)


# -----------------------------------------------------------------------
# Practical 2 — Downsampling (/api/p2/...)
# -----------------------------------------------------------------------

def _p2():
    from app.processors import p02_downsampling
    return p02_downsampling


@api_bp.route('/p2/downsample', methods=['POST'])
def p2_downsample():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    steps = int(data.get('steps', 5))
    result = _p2().downsample_series(data['filename'], steps=steps)
    if result is None:
        return jsonify({"error": "Failed to downsample image"}), 400
    return jsonify(result)


@api_bp.route('/p2/downsample-plot', methods=['POST'])
def p2_downsample_plot():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p2().downsample_comparison_plot(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate plot"}), 400
    return jsonify(result)


@api_bp.route('/p2/upscale-compare', methods=['POST'])
def p2_upscale_compare():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p2().upscale_comparison_plot(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate comparison"}), 400
    return jsonify(result)


# -----------------------------------------------------------------------
# Practical 3 — Negation, Subtraction, Inversion (/api/p3/...)
# -----------------------------------------------------------------------

def _p3():
    from app.processors import p03_negation_subtraction
    return p03_negation_subtraction


@api_bp.route('/p3/pairs')
def p3_pairs():
    """Return recommended image pairs for subtraction."""
    return jsonify({"pairs": _p3().RECOMMENDED_PAIRS})


@api_bp.route('/p3/negate', methods=['POST'])
def p3_negate():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p3().compute_negation(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to compute negation"}), 400
    return jsonify(result)


@api_bp.route('/p3/subtract', methods=['POST'])
def p3_subtract():
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2'"}), 400
    result = _p3().compute_subtraction(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to compute subtraction"}), 400
    return jsonify(result)


@api_bp.route('/p3/pipeline', methods=['POST'])
def p3_pipeline():
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2'"}), 400
    result = _p3().compute_pipeline(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to run pipeline"}), 400
    return jsonify(result)


# -----------------------------------------------------------------------
# Practical 4 — Gamma Correction (/api/p4/...)
# -----------------------------------------------------------------------

def _p4():
    from app.processors import p04_gamma
    return p04_gamma


@api_bp.route('/p4/gamma', methods=['POST'])
def p4_gamma():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    gamma = float(data.get('gamma', 1.0))
    c = float(data.get('c', 1.0))
    result = _p4().apply_gamma(data['filename'], gamma=gamma, c=c)
    if result is None:
        return jsonify({"error": "Failed to apply gamma"}), 400
    return jsonify(result)


@api_bp.route('/p4/gamma-series', methods=['POST'])
def p4_gamma_series():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    gammas = data.get('gammas', None)
    if gammas:
        gammas = [float(g) for g in gammas]
    result = _p4().gamma_series(data['filename'], gammas=gammas)
    if result is None:
        return jsonify({"error": "Failed to generate gamma series"}), 400
    return jsonify(result)


@api_bp.route('/p4/log-transform', methods=['POST'])
def p4_log_transform():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    result = _p4().log_transform(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to apply log transform"}), 400
    return jsonify(result)


@api_bp.route('/p4/curves')
def p4_curves():
    result = _p4().transformation_curves()
    return jsonify(result)


@api_bp.route('/p4/contrast', methods=['POST'])
def p4_contrast():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    mode = data.get('mode', 'dark')
    gammas = data.get('gammas', None)
    if gammas:
        gammas = [float(g) for g in gammas]
    result = _p4().contrast_enhancement(data['filename'], gammas=gammas, mode=mode)
    if result is None:
        return jsonify({"error": "Failed to enhance contrast"}), 400
    return jsonify(result)
