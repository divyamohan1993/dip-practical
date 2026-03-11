"""
Digital Image Processing Practical Web Application
Course: CSU2543 | Faculty: Ishani Sharma | Shoolini University
Student: Divya Mohan | BTech CSE Cybersecurity | Semester 8
"""

from flask import Flask


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    from app.routes.pages import pages_bp
    from app.routes.api import api_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
