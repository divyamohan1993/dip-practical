"""
Digital Image Processing Practical Web Application
Course: CSU2543 | Faculty: Ishani Sharma | Shoolini University
Student: Divya Mohan | BTech CSE Cybersecurity | Semester 8
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from app.image_processor import (
    get_available_images,
    compute_spatial_difference,
    generate_histogram,
    generate_comparison_plot,
    generate_matplotlib_demo,
    RECOMMENDED_PAIRS,
    MATPLOTLIB_REFERENCE,
    load_image,
    image_to_base64_png,
)

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/api/images')
def api_images():
    """List all available images with metadata."""
    images = get_available_images()
    return jsonify({
        "images": images,
        "count": len(images),
        "recommended_pairs": RECOMMENDED_PAIRS
    })


@app.route('/api/image/<path:filename>')
def api_image(filename):
    """Serve a specific image as base64 PNG."""
    img = load_image(filename)
    if img is None:
        return jsonify({"error": f"Image not found: {filename}"}), 404
    b64 = image_to_base64_png(img)
    return jsonify({"image": b64, "filename": filename})


@app.route('/api/spatial-difference', methods=['POST'])
def api_spatial_difference():
    """Compute spatial difference between two images."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400

    result = compute_spatial_difference(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to process images. Check filenames."}), 400

    return jsonify(result)


@app.route('/api/histogram', methods=['POST'])
def api_histogram():
    """Generate histogram for an image."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Provide 'filename'"}), 400

    result = generate_histogram(data['filename'])
    if result is None:
        return jsonify({"error": "Failed to generate histogram"}), 400

    return jsonify({"histogram": result})


@app.route('/api/comparison-plot', methods=['POST'])
def api_comparison_plot():
    """Generate a full comparison plot."""
    data = request.get_json()
    if not data or 'image1' not in data or 'image2' not in data:
        return jsonify({"error": "Provide 'image1' and 'image2' filenames"}), 400

    result = generate_comparison_plot(data['image1'], data['image2'])
    if result is None:
        return jsonify({"error": "Failed to generate comparison plot"}), 400

    return jsonify({"plot": result})


@app.route('/api/matplotlib-reference')
def api_matplotlib_reference():
    """Return comprehensive matplotlib reference."""
    return jsonify(MATPLOTLIB_REFERENCE)


@app.route('/api/matplotlib-demos')
def api_matplotlib_demos():
    """Generate and return matplotlib demonstration plots."""
    demos = generate_matplotlib_demo()
    return jsonify({"demos": demos})


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "dip-practical"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
