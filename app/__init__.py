"""
Digital Image Processing Practical Web Application
Course: CSU2543 | Faculty: Ishani Sharma | Shoolini University
Student: Divya Mohan | BTech CSE Cybersecurity | Semester 8
"""

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Honour X-Forwarded-* headers from Cloud Run / Cloudflare so request.url
    # reflects the user-facing https URL (e.g. https://dip.dmj.one/practical/7)
    # instead of the internal http hop. Critical for the cover-page QR codes.
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    from app.routes.pages import pages_bp
    from app.routes.api import api_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
