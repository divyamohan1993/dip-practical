"""
Page routes for DIP Practical web application.
Serves HTML templates for the main page, individual practicals, and health check.
"""

from flask import Blueprint, render_template, jsonify
from jinja2 import TemplateNotFound

pages_bp = Blueprint('pages', __name__)

PRACTICAL_META = {
    1: {"title": "Loading & Displaying Images", "chapter": "G&W Ch 2"},
    2: {"title": "Impact of Sampling Rate on Spatial Resolution", "chapter": "G&W Ch 2"},
    3: {"title": "Image Negation, Subtraction & Inversion", "chapter": "G&W Ch 2-3"},
    4: {"title": "Gamma Correction & Power Law Transformations", "chapter": "G&W Ch 3"},
}


@pages_bp.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@pages_bp.route('/practical/<int:num>')
def practical(num):
    """Serve an individual practical page (1-4)."""
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
