"""
Page routes for DIP Practical web application.
Serves HTML templates for the main page, individual practicals, and health check.
"""

from flask import Blueprint, render_template, jsonify
from jinja2 import TemplateNotFound

pages_bp = Blueprint('pages', __name__)

PRACTICAL_META = {
    1: {"title": "Image Fundamentals & Spatial Differencing", "chapter": "G&W Ch 2"},
    2: {"title": "Image Subtraction & Inversion", "chapter": "G&W Ch 2-3"},
    3: {"title": "Histogram Equalization & CLAHE", "chapter": "G&W Ch 3.3"},
    4: {"title": "Spatial Filtering", "chapter": "G&W Ch 3.5-3.7"},
    5: {"title": "Frequency Domain Filtering", "chapter": "G&W Ch 4"},
    6: {"title": "Image Restoration & Noise", "chapter": "G&W Ch 5"},
    7: {"title": "Color Image Processing", "chapter": "G&W Ch 6"},
    8: {"title": "Morphological Operations", "chapter": "G&W Ch 9"},
    9: {"title": "Edge Detection & Segmentation", "chapter": "G&W Ch 10"},
    10: {"title": "Image Compression", "chapter": "G&W Ch 8"},
}


@pages_bp.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@pages_bp.route('/practical/<int:num>')
def practical(num):
    """Serve an individual practical page (1-10)."""
    if num not in PRACTICAL_META:
        return jsonify({"error": f"Practical {num} not found"}), 404

    try:
        return render_template(f'practicals/p{num:02d}.html')
    except TemplateNotFound:
        meta = PRACTICAL_META[num]
        return render_template(
            'practicals/_coming_soon.html',
            num=num,
            title=meta["title"],
            chapter=meta["chapter"],
        )


@pages_bp.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "dip-practical"})
