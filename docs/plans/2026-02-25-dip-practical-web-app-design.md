# DIP Practical Web Application - Design Document

**Date**: 2026-02-25
**Student**: Divya Mohan | BTech CSE Cybersecurity | Semester 8
**University**: Shoolini University
**Course**: Digital Image Processing [CSU2543]
**Faculty**: Ishani Sharma

## Architecture

Flask backend + vanilla HTML/CSS/JS frontend with skeuomorphic design.

### Stack
- **Backend**: Flask + Gunicorn, OpenCV (cv2), Matplotlib, NumPy
- **Frontend**: Vanilla HTML/CSS/JS, skeuomorphic UI
- **Server**: GCP e2-medium spot, asia-south2 (Delhi), Ubuntu 24.04
- **Proxy**: Nginx reverse proxy → Gunicorn (port 8000)
- **Domain**: dip.dmj.one → Cloudflare proxy → GCP instance (HTTP)
- **Repo**: github.com/divyamohan1993/dip-practical

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Main page |
| GET | `/api/images` | List all available images with metadata |
| GET | `/api/image/<name>` | Serve a specific image as PNG |
| POST | `/api/spatial-difference` | Compute abs difference between two images |
| POST | `/api/histogram` | Generate histogram for an image |
| GET | `/api/matplotlib-reference` | Return matplotlib command reference data |

## Frontend Sections

1. **Hero/Header**: University branding, course details, student info
2. **Practical 1 - Spatial Image Differencing**:
   - Image gallery browser (all CH02 images)
   - Interactive pair selector with live preview
   - Spatial difference computation with result display
   - Explanation of the math behind absdiff
   - Related image pairs highlighted (angiography, dental, tungsten, einstein contrast)
3. **Matplotlib Reference**:
   - Comprehensive command documentation with categories
   - subplot, imshow, title, axis, colorbar, figure, savefig, etc.
   - Live-generated example plots from the server
4. **Practical 2**: Placeholder section, styled "Coming Soon"
5. **Footer**: Credits, Shoolini University, academic context

## GCP Setup

- e2-medium spot (2 vCPU, 4GB RAM), asia-south2-a
- Ubuntu 24.04 LTS
- autoconfig.sh: idempotent zero-intervention deploy
- nginx → gunicorn (4 workers) → Flask
- UFW: 80, 22
- systemd service for the app

## Image Processing Details

### Meaningful Image Pairs (CH02)
1. **Angiography**: mask (Fig0228a) vs live (Fig0228b) - classic digital subtraction
2. **Dental X-ray**: original (Fig0230a) vs mask (Fig0230b)
3. **Tungsten**: filament (Fig0229a) vs sensor shading (Fig0229b)
4. **Einstein Contrast**: low (Fig0241a) vs med (Fig0241b) vs high (Fig0241c)

### Processing Pipeline
1. Load TIF with cv2.imread (grayscale)
2. Resize if dimensions differ (cv2.resize with INTER_AREA)
3. cv2.absdiff() for spatial difference
4. Convert to PNG for browser display (base64 or served endpoint)
5. Generate histograms with matplotlib
