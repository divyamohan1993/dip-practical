"""
API routes for DIP Practical web application.
All endpoints are registered under the /api prefix via the blueprint.
"""

from flask import Blueprint, jsonify, request

from app.processors.common import (
    get_chapters, get_chapter_images, load_image, image_to_base64_png,
    get_available_images,
)

api_bp = Blueprint('api', __name__)


# -----------------------------------------------------------------------
# Chapter & Image endpoints
# -----------------------------------------------------------------------

@api_bp.route('/chapters')
def api_chapters():
    """List all available chapters with download status."""
    chapters = get_chapters()
    return jsonify({"chapters": chapters})


@api_bp.route('/chapters/<chapter_id>/images')
def api_chapter_images(chapter_id):
    """List images in a chapter. Downloads the chapter on first access."""
    images = get_chapter_images(chapter_id)
    return jsonify({"images": images, "chapter": chapter_id, "count": len(images)})


@api_bp.route('/images')
def api_images():
    """Legacy: list images from a single chapter (default CH02)."""
    chapter = request.args.get('chapter', 'CH02')
    images = get_available_images(chapter)
    return jsonify({"images": images, "count": len(images)})


@api_bp.route('/image/<path:filename>')
def api_image(filename):
    """Serve a specific image as base64 PNG."""
    chapter = request.args.get('chapter', 'CH02')
    img = load_image(filename, chapter)
    if img is None:
        return jsonify({"error": f"Image not found: {filename}"}), 404
    b64 = image_to_base64_png(img)
    return jsonify({"image": b64, "filename": filename, "chapter": chapter})


def _get_img_params(data, prefix=''):
    """Extract chapter + filename from request data."""
    ch = data.get(f'{prefix}chapter', 'CH02')
    fn = data.get(f'{prefix}filename', data.get(f'{prefix}image', ''))
    return ch, fn


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
    chapter = data.get('chapter', 'CH02')
    result = _p1().display_image(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to load image"}), 400
    return jsonify(result)


@api_bp.route('/p1/histogram', methods=['POST'])
def p1_histogram():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p1().display_histogram(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to generate histogram"}), 400
    return jsonify(result)


@api_bp.route('/p1/multi-display', methods=['POST'])
def p1_multi_display():
    data = request.get_json()
    images = data.get('images') if data else None
    if not images:
        return jsonify({"error": "Provide 'images' array of {chapter, filename}"}), 400
    result = _p1().display_multiple(images)
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
    chapter = data.get('chapter', 'CH02')
    steps = int(data.get('steps', 5))
    result = _p2().downsample_series(data['filename'], chapter=chapter, steps=steps)
    if result is None:
        return jsonify({"error": "Failed to downsample image"}), 400
    return jsonify(result)


@api_bp.route('/p2/downsample-plot', methods=['POST'])
def p2_downsample_plot():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p2().downsample_comparison_plot(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to generate plot"}), 400
    return jsonify(result)


@api_bp.route('/p2/upscale-compare', methods=['POST'])
def p2_upscale_compare():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p2().upscale_comparison_plot(data['filename'], chapter=chapter)
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
    chapter = data.get('chapter', 'CH02')
    result = _p3().compute_negation(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to compute negation"}), 400
    return jsonify(result)


@api_bp.route('/p3/subtract', methods=['POST'])
def p3_subtract():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Provide image data"}), 400
    image1 = data.get('image1', data.get('filename1', ''))
    image2 = data.get('image2', data.get('filename2', ''))
    chapter1 = data.get('chapter1', 'CH02')
    chapter2 = data.get('chapter2', 'CH02')
    if not image1 or not image2:
        return jsonify({"error": "Provide both images"}), 400
    result = _p3().compute_subtraction(image1, image2, chapter1=chapter1, chapter2=chapter2)
    if result is None:
        return jsonify({"error": "Failed to compute subtraction"}), 400
    return jsonify(result)


@api_bp.route('/p3/pipeline', methods=['POST'])
def p3_pipeline():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Provide image data"}), 400
    image1 = data.get('image1', data.get('filename1', ''))
    image2 = data.get('image2', data.get('filename2', ''))
    chapter1 = data.get('chapter1', 'CH02')
    chapter2 = data.get('chapter2', 'CH02')
    if not image1 or not image2:
        return jsonify({"error": "Provide both images"}), 400
    result = _p3().compute_pipeline(image1, image2, chapter1=chapter1, chapter2=chapter2)
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
    chapter = data.get('chapter', 'CH02')
    gamma = float(data.get('gamma', 1.0))
    c = float(data.get('c', 1.0))
    result = _p4().apply_gamma(data['filename'], chapter=chapter, gamma=gamma, c=c)
    if result is None:
        return jsonify({"error": "Failed to apply gamma"}), 400
    return jsonify(result)


@api_bp.route('/p4/gamma-series', methods=['POST'])
def p4_gamma_series():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    gammas = data.get('gammas', None)
    if gammas:
        gammas = [float(g) for g in gammas]
    result = _p4().gamma_series(data['filename'], chapter=chapter, gammas=gammas)
    if result is None:
        return jsonify({"error": "Failed to generate gamma series"}), 400
    return jsonify(result)


@api_bp.route('/p4/log-transform', methods=['POST'])
def p4_log_transform():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p4().log_transform(data['filename'], chapter=chapter)
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
    chapter = data.get('chapter', 'CH02')
    mode = data.get('mode', 'dark')
    gammas = data.get('gammas', None)
    if gammas:
        gammas = [float(g) for g in gammas]
    result = _p4().contrast_enhancement(data['filename'], chapter=chapter, gammas=gammas, mode=mode)
    if result is None:
        return jsonify({"error": "Failed to enhance contrast"}), 400
    return jsonify(result)


# -----------------------------------------------------------------------
# Practical 5 — Histogram Equalization (/api/p5/...)
# -----------------------------------------------------------------------

def _p5():
    from app.processors import p05_histogram_eq
    return p05_histogram_eq


@api_bp.route('/p5/original-histogram', methods=['POST'])
def p5_original_histogram():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p5().compute_original_histogram(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to compute histogram"}), 400
    return jsonify(result)


@api_bp.route('/p5/equalize', methods=['POST'])
def p5_equalize():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p5().compute_equalization(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to equalize histogram"}), 400
    return jsonify(result)


@api_bp.route('/p5/transfer-function', methods=['POST'])
def p5_transfer_function():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400
    chapter = data.get('chapter', 'CH02')
    result = _p5().compute_transfer_function(data['filename'], chapter=chapter)
    if result is None:
        return jsonify({"error": "Failed to compute transfer function"}), 400
    return jsonify(result)


@api_bp.route('/p5/multi-equalize', methods=['POST'])
def p5_multi_equalize():
    data = request.get_json()
    images = data.get('images') if data else None
    if not images:
        return jsonify({"error": "Provide 'images' array of {chapter, filename}"}), 400
    result = _p5().compute_multi_equalize(images)
    if result is None:
        return jsonify({"error": "Failed to equalize images"}), 400
    return jsonify(result)
