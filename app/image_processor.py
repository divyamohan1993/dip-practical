"""
Image processing module for DIP Practical.
Handles loading TIF images, computing spatial differences,
generating histograms, and matplotlib demonstrations.
"""

import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import os
from pathlib import Path


IMAGES_DIR = Path(__file__).parent.parent / "DIP3E_CH02_Original_Images" / "DIP3E_Original_Images_CH02"

# Curated image pairs that produce meaningful spatial differences
RECOMMENDED_PAIRS = [
    {
        "id": "angiography",
        "name": "Digital Subtraction Angiography",
        "description": "Classic medical imaging technique. The mask image (pre-contrast) is subtracted from the live image (post-contrast injection) to isolate blood vessels. This is one of the most important applications of image subtraction in medical imaging.",
        "image1": "Fig0228(a)(angiography_mask_image).tif",
        "image2": "Fig0228(b)(angiography_live_ image).tif",
        "theory": "Digital Subtraction Angiography (DSA) works by acquiring a 'mask' image before contrast agent injection, then a 'live' image after injection. Subtracting mask from live removes static anatomy (bones, soft tissue), leaving only the contrast-filled vessels visible. Mathematically: g(x,y) = |f_live(x,y) - f_mask(x,y)|"
    },
    {
        "id": "dental_xray",
        "name": "Dental X-ray Subtraction",
        "description": "Dental radiograph subtraction reveals changes between visits (bone loss, lesion progression). The original X-ray and its mask are subtracted to enhance diagnostic features.",
        "image1": "Fig0230(a)(dental_xray).tif",
        "image2": "Fig0230(b)(dental_xray_mask).tif",
        "theory": "Dental subtraction radiography is used to detect subtle changes in bone density between patient visits. By subtracting a baseline radiograph from a follow-up image, clinicians can identify areas of bone loss or regeneration that might be invisible in individual images."
    },
    {
        "id": "tungsten",
        "name": "Shading Correction (Tungsten Filament)",
        "description": "Demonstrates shading correction by subtracting non-uniform illumination. The sensor shading pattern is removed from the filament image to produce a uniformly illuminated result.",
        "image1": "Fig0229(a)(tungsten_filament_shaded).tif",
        "image2": "Fig0229(b)(tungsten_sensor_shading).tif",
        "theory": "Shading correction compensates for non-uniform sensor response or illumination. If f(x,y) is the shaded image and s(x,y) is the shading pattern, then the corrected image is approximately f(x,y) - s(x,y). This is essential in microscopy, astronomical imaging, and industrial inspection."
    },
    {
        "id": "einstein_low_med",
        "name": "Einstein: Low vs Medium Contrast",
        "description": "Compares the same Einstein portrait at different contrast levels. The difference reveals which regions gain or lose intensity as contrast increases.",
        "image1": "Fig0241(a)(einstein low contrast).tif",
        "image2": "Fig0241(b)(einstein med contrast).tif",
        "theory": "Contrast is the difference in luminance that makes an object distinguishable. Comparing images at different contrast levels through subtraction reveals how pixel intensities are redistributed. This is fundamental to understanding contrast enhancement techniques like histogram equalization."
    },
    {
        "id": "einstein_med_high",
        "name": "Einstein: Medium vs High Contrast",
        "description": "Continues the contrast analysis. Subtracting medium from high contrast shows the most extreme intensity redistributions.",
        "image1": "Fig0241(b)(einstein med contrast).tif",
        "image2": "Fig0241(c)(einstein high contrast).tif",
        "theory": "As contrast increases, the histogram of the image stretches to cover a wider range of intensity values. The spatial difference between medium and high contrast versions highlights edges and texture regions where intensity changes are most dramatic."
    },
    {
        "id": "einstein_low_high",
        "name": "Einstein: Low vs High Contrast",
        "description": "Maximum contrast difference. Shows the full range of intensity redistribution from lowest to highest contrast version.",
        "image1": "Fig0241(a)(einstein low contrast).tif",
        "image2": "Fig0241(c)(einstein high contrast).tif",
        "theory": "The maximum spatial difference between low and high contrast versions reveals the complete transformation applied. This difference image essentially visualizes the 'contrast enhancement function' applied spatially across the image."
    }
]


def get_available_images():
    """Return list of available images with metadata."""
    images = []
    if not IMAGES_DIR.exists():
        return images

    for f in sorted(IMAGES_DIR.iterdir()):
        if f.suffix.lower() == '.tif':
            img = cv2.imread(str(f), cv2.IMREAD_GRAYSCALE)
            if img is not None:
                h, w = img.shape
                images.append({
                    "filename": f.name,
                    "width": w,
                    "height": h,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                    "display_name": _parse_image_name(f.name)
                })
    return images


def _parse_image_name(filename):
    """Extract a human-readable name from the filename."""
    name = filename.replace('.tif', '')
    # Extract figure number and description
    if '(' in name:
        parts = name.split('(', 1)
        fig_num = parts[0].strip()
        desc = parts[1].rstrip(')')
        # Clean up nested parentheses
        desc = desc.replace('(', ' - ').replace(')', '')
        return f"{fig_num}: {desc}"
    return name


def load_image(filename):
    """Load a TIF image as grayscale numpy array."""
    path = IMAGES_DIR / filename
    if not path.exists():
        return None
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return img


def image_to_base64_png(img):
    """Convert numpy array to base64-encoded PNG string."""
    if img is None:
        return None
    success, buffer = cv2.imencode('.png', img)
    if not success:
        return None
    return base64.b64encode(buffer).decode('utf-8')


def compute_spatial_difference(filename1, filename2):
    """
    Compute absolute spatial difference between two images.
    Returns dict with original images, difference image, and statistics.
    """
    img1 = load_image(filename1)
    img2 = load_image(filename2)

    if img1 is None or img2 is None:
        return None

    # Resize if dimensions differ
    resized = False
    original_shapes = {"img1": img1.shape, "img2": img2.shape}
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]),
                           interpolation=cv2.INTER_AREA)
        resized = True

    # Compute absolute difference
    diff = cv2.absdiff(img1, img2)

    # Compute enhanced difference (stretched to full range for visibility)
    if diff.max() > 0:
        diff_enhanced = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    else:
        diff_enhanced = diff.copy()

    # Statistics
    stats = {
        "mean_difference": float(np.mean(diff)),
        "max_difference": int(np.max(diff)),
        "min_difference": int(np.min(diff)),
        "std_difference": float(np.std(diff)),
        "nonzero_pixels": int(np.count_nonzero(diff)),
        "total_pixels": int(diff.size),
        "nonzero_percentage": round(float(np.count_nonzero(diff)) / diff.size * 100, 2),
        "resized": resized,
        "original_shapes": {
            "image1": list(original_shapes["img1"]),
            "image2": list(original_shapes["img2"])
        },
        "final_shape": list(img1.shape)
    }

    return {
        "image1": image_to_base64_png(img1),
        "image2": image_to_base64_png(img2),
        "difference": image_to_base64_png(diff),
        "difference_enhanced": image_to_base64_png(diff_enhanced),
        "stats": stats
    }


def generate_histogram(filename):
    """Generate histogram for an image, returned as base64 PNG."""
    img = load_image(filename)
    if img is None:
        return None

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    # Image display
    axes[0].imshow(img, cmap='gray')
    axes[0].set_title(f'{_parse_image_name(filename)}', fontsize=10)
    axes[0].axis('off')

    # Histogram
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    axes[1].plot(hist, color='#2c3e50', linewidth=1.2)
    axes[1].fill_between(range(256), hist.flatten(), alpha=0.3, color='#3498db')
    axes[1].set_xlim([0, 256])
    axes[1].set_xlabel('Pixel Intensity', fontsize=10)
    axes[1].set_ylabel('Frequency', fontsize=10)
    axes[1].set_title('Intensity Histogram', fontsize=10)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor='#fafafa', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def generate_comparison_plot(filename1, filename2):
    """Generate a comprehensive comparison plot with originals, difference, and histograms."""
    img1 = load_image(filename1)
    img2 = load_image(filename2)

    if img1 is None or img2 is None:
        return None

    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]),
                           interpolation=cv2.INTER_AREA)

    diff = cv2.absdiff(img1, img2)
    diff_enhanced = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX) if diff.max() > 0 else diff

    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    fig.suptitle('Spatial Difference Analysis', fontsize=14, fontweight='bold', y=0.98)

    # Row 1: Images
    axes[0, 0].imshow(img1, cmap='gray')
    axes[0, 0].set_title(f'Image 1\n{_parse_image_name(filename1)}', fontsize=9)
    axes[0, 0].axis('off')

    axes[0, 1].imshow(img2, cmap='gray')
    axes[0, 1].set_title(f'Image 2\n{_parse_image_name(filename2)}', fontsize=9)
    axes[0, 1].axis('off')

    axes[0, 2].imshow(diff, cmap='gray')
    axes[0, 2].set_title('Absolute Difference\n|Image1 - Image2|', fontsize=9)
    axes[0, 2].axis('off')

    im = axes[0, 3].imshow(diff_enhanced, cmap='hot')
    axes[0, 3].set_title('Enhanced Difference\n(Heatmap)', fontsize=9)
    axes[0, 3].axis('off')
    plt.colorbar(im, ax=axes[0, 3], fraction=0.046, pad=0.04)

    # Row 2: Histograms
    hist1 = cv2.calcHist([img1], [0], None, [256], [0, 256])
    axes[1, 0].plot(hist1, color='#2c3e50', linewidth=1)
    axes[1, 0].fill_between(range(256), hist1.flatten(), alpha=0.3, color='#3498db')
    axes[1, 0].set_title('Histogram - Image 1', fontsize=9)
    axes[1, 0].set_xlim([0, 256])
    axes[1, 0].grid(True, alpha=0.3)

    hist2 = cv2.calcHist([img2], [0], None, [256], [0, 256])
    axes[1, 1].plot(hist2, color='#2c3e50', linewidth=1)
    axes[1, 1].fill_between(range(256), hist2.flatten(), alpha=0.3, color='#e74c3c')
    axes[1, 1].set_title('Histogram - Image 2', fontsize=9)
    axes[1, 1].set_xlim([0, 256])
    axes[1, 1].grid(True, alpha=0.3)

    hist_diff = cv2.calcHist([diff], [0], None, [256], [0, 256])
    axes[1, 2].plot(hist_diff, color='#2c3e50', linewidth=1)
    axes[1, 2].fill_between(range(256), hist_diff.flatten(), alpha=0.3, color='#2ecc71')
    axes[1, 2].set_title('Histogram - Difference', fontsize=9)
    axes[1, 2].set_xlim([0, 256])
    axes[1, 2].grid(True, alpha=0.3)

    # Overlay histograms
    axes[1, 3].plot(hist1, color='#3498db', linewidth=1, label='Image 1', alpha=0.7)
    axes[1, 3].plot(hist2, color='#e74c3c', linewidth=1, label='Image 2', alpha=0.7)
    axes[1, 3].plot(hist_diff, color='#2ecc71', linewidth=1, label='Difference', alpha=0.7)
    axes[1, 3].set_title('Overlay Comparison', fontsize=9)
    axes[1, 3].set_xlim([0, 256])
    axes[1, 3].legend(fontsize=8)
    axes[1, 3].grid(True, alpha=0.3)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def generate_matplotlib_demo():
    """Generate demonstration plots showing various matplotlib capabilities."""
    demos = {}

    # Demo 1: Subplot layouts
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    fig.suptitle('plt.subplot() - Grid Layouts', fontsize=13, fontweight='bold')

    x = np.linspace(0, 2 * np.pi, 200)
    styles = [
        ('Line Plot', lambda ax: ax.plot(x, np.sin(x), 'b-', linewidth=2)),
        ('Scatter', lambda ax: ax.scatter(np.random.rand(50), np.random.rand(50), c=np.random.rand(50), cmap='viridis', s=60, alpha=0.7)),
        ('Bar Chart', lambda ax: ax.bar(['A', 'B', 'C', 'D'], [3, 7, 2, 5], color=['#e74c3c', '#3498db', '#2ecc71', '#f39c12'])),
        ('Histogram', lambda ax: ax.hist(np.random.randn(500), bins=30, color='#9b59b6', alpha=0.7, edgecolor='white')),
        ('Filled Plot', lambda ax: (ax.fill_between(x, np.sin(x), np.cos(x), alpha=0.3, color='#e74c3c'), ax.plot(x, np.sin(x), 'r-'), ax.plot(x, np.cos(x), 'b-'))),
        ('Step Plot', lambda ax: ax.step(range(10), np.random.randint(1, 10, 10), where='mid', color='#1abc9c', linewidth=2)),
    ]

    for ax, (title, plot_fn) in zip(axes.flat, styles):
        plot_fn(ax)
        ax.set_title(title, fontsize=10)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    demos['subplot_layouts'] = base64.b64encode(buf.read()).decode('utf-8')

    # Demo 2: Colormaps on image data
    img = load_image('Fig0219(rose1024).tif')
    if img is not None:
        cmaps = ['gray', 'hot', 'viridis', 'plasma', 'inferno', 'coolwarm']
        fig, axes = plt.subplots(2, 3, figsize=(14, 9))
        fig.suptitle('plt.imshow() with Different Colormaps', fontsize=13, fontweight='bold')

        for ax, cmap_name in zip(axes.flat, cmaps):
            im = ax.imshow(img, cmap=cmap_name)
            ax.set_title(f"cmap='{cmap_name}'", fontsize=10)
            ax.axis('off')
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        plt.close(fig)
        buf.seek(0)
        demos['colormaps'] = base64.b64encode(buf.read()).decode('utf-8')

    # Demo 3: Figure customization
    fig = plt.figure(figsize=(12, 5))
    fig.suptitle('plt.figure() Customization & Annotations', fontsize=13, fontweight='bold')

    ax1 = fig.add_subplot(121)
    t = np.linspace(0, 4 * np.pi, 300)
    ax1.plot(t, np.sin(t), 'b-', label='sin(t)', linewidth=2)
    ax1.plot(t, np.cos(t), 'r--', label='cos(t)', linewidth=2)
    ax1.axhline(y=0, color='k', linewidth=0.5)
    ax1.axvline(x=np.pi, color='gray', linestyle=':', linewidth=1)
    ax1.annotate('Peak', xy=(np.pi/2, 1), xytext=(np.pi/2 + 1, 1.3),
                arrowprops=dict(arrowstyle='->', color='#e74c3c'),
                fontsize=10, color='#e74c3c')
    ax1.set_xlabel('Time (radians)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Trigonometric Functions')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)

    ax2 = fig.add_subplot(122, projection='polar')
    theta = np.linspace(0, 2 * np.pi, 100)
    r = 1 + np.cos(3 * theta)
    ax2.plot(theta, r, 'g-', linewidth=2)
    ax2.fill(theta, r, alpha=0.2, color='green')
    ax2.set_title('Polar Plot: r = 1 + cos(3\u03b8)', pad=20)

    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    buf.seek(0)
    demos['figure_customization'] = base64.b64encode(buf.read()).decode('utf-8')

    return demos


# Comprehensive matplotlib reference data
MATPLOTLIB_REFERENCE = {
    "categories": [
        {
            "name": "Figure & Layout",
            "commands": [
                {
                    "command": "plt.figure(figsize, dpi, facecolor)",
                    "description": "Creates a new figure. figsize=(width, height) in inches, dpi controls resolution, facecolor sets background.",
                    "example": "fig = plt.figure(figsize=(10, 6), dpi=120)",
                    "tip": "Always set figsize for consistent output across displays."
                },
                {
                    "command": "plt.subplot(nrows, ncols, index)",
                    "description": "Adds a subplot to the current figure. Grid of nrows x ncols, index is 1-based position.",
                    "example": "plt.subplot(2, 3, 1)  # 2x3 grid, position 1 (top-left)",
                    "tip": "Can also use shorthand: plt.subplot(231)"
                },
                {
                    "command": "plt.subplots(nrows, ncols)",
                    "description": "Creates figure and array of Axes in one call. Returns (fig, axes) tuple.",
                    "example": "fig, axes = plt.subplots(2, 2, figsize=(10, 10))",
                    "tip": "Preferred over repeated subplot() calls. axes is a 2D array for grid access."
                },
                {
                    "command": "plt.tight_layout(pad)",
                    "description": "Automatically adjusts subplot spacing to prevent overlap. pad controls padding.",
                    "example": "plt.tight_layout(pad=1.5)",
                    "tip": "Call this before plt.show() or plt.savefig()."
                },
                {
                    "command": "fig.add_subplot(pos, projection)",
                    "description": "Adds subplot with optional projection (e.g., 'polar', '3d').",
                    "example": "ax = fig.add_subplot(111, projection='polar')",
                    "tip": "Use for mixed projections in the same figure."
                },
                {
                    "command": "plt.GridSpec(nrows, ncols)",
                    "description": "Advanced grid layout specification for unequal subplot sizes.",
                    "example": "gs = plt.GridSpec(2, 3); ax1 = fig.add_subplot(gs[0, :])",
                    "tip": "Use slicing to span multiple grid cells."
                }
            ]
        },
        {
            "name": "Image Display",
            "commands": [
                {
                    "command": "plt.imshow(X, cmap, vmin, vmax, interpolation)",
                    "description": "Displays a 2D array as an image. cmap maps values to colors. vmin/vmax clip the colormap range.",
                    "example": "plt.imshow(image, cmap='gray', vmin=0, vmax=255)",
                    "tip": "For grayscale images, always specify cmap='gray' to avoid default color mapping."
                },
                {
                    "command": "plt.colorbar(mappable, ax, fraction, pad)",
                    "description": "Adds a color scale bar to the plot, showing the mapping between data values and colors.",
                    "example": "im = plt.imshow(data, cmap='hot'); plt.colorbar(im)",
                    "tip": "fraction=0.046, pad=0.04 gives a well-proportioned colorbar."
                },
                {
                    "command": "plt.axis('off')",
                    "description": "Hides all axis lines, tick marks, and labels. Essential for clean image display.",
                    "example": "plt.imshow(img, cmap='gray'); plt.axis('off')",
                    "tip": "Always use when displaying images to remove distracting borders."
                }
            ]
        },
        {
            "name": "Plotting Functions",
            "commands": [
                {
                    "command": "plt.plot(x, y, fmt, linewidth, label)",
                    "description": "Creates a 2D line plot. fmt is a format string (e.g., 'r--' for red dashed). label is for legend.",
                    "example": "plt.plot(x, y, 'b-', linewidth=2, label='Signal')",
                    "tip": "Format: '[color][marker][linestyle]'. 'r-o' = red solid with circles."
                },
                {
                    "command": "plt.scatter(x, y, c, s, cmap, alpha)",
                    "description": "Creates a scatter plot. c maps point colors, s controls size, alpha is transparency.",
                    "example": "plt.scatter(x, y, c=values, cmap='viridis', s=50, alpha=0.7)",
                    "tip": "c can be a single color or an array for color-mapped data."
                },
                {
                    "command": "plt.bar(x, height, color, width, edgecolor)",
                    "description": "Creates vertical bar chart. x is position, height is bar heights.",
                    "example": "plt.bar(['A', 'B', 'C'], [10, 20, 15], color='steelblue')",
                    "tip": "Use plt.barh() for horizontal bars."
                },
                {
                    "command": "plt.hist(x, bins, color, alpha, edgecolor)",
                    "description": "Creates a histogram showing data distribution. bins controls the number of intervals.",
                    "example": "plt.hist(data, bins=50, color='purple', alpha=0.7, edgecolor='white')",
                    "tip": "Use density=True for normalized histograms (probability density)."
                },
                {
                    "command": "plt.fill_between(x, y1, y2, alpha, color)",
                    "description": "Fills the area between two curves y1 and y2.",
                    "example": "plt.fill_between(x, 0, y, alpha=0.3, color='blue')",
                    "tip": "Great for confidence intervals and area charts."
                },
                {
                    "command": "plt.contour(X, Y, Z, levels) / plt.contourf()",
                    "description": "Creates contour lines (contour) or filled contour plots (contourf) from 2D data.",
                    "example": "plt.contourf(X, Y, Z, levels=20, cmap='RdBu')",
                    "tip": "Pair with plt.colorbar() for scale reference."
                }
            ]
        },
        {
            "name": "Labels & Annotations",
            "commands": [
                {
                    "command": "plt.title(label, fontsize, fontweight, pad)",
                    "description": "Sets the title of the current axes/subplot.",
                    "example": "plt.title('Spatial Difference Analysis', fontsize=14, fontweight='bold')",
                    "tip": "Use fig.suptitle() for an overall figure title above all subplots."
                },
                {
                    "command": "plt.xlabel(label) / plt.ylabel(label)",
                    "description": "Sets axis labels with optional fontsize and style parameters.",
                    "example": "plt.xlabel('Pixel Intensity', fontsize=12)",
                    "tip": "Use LaTeX: plt.xlabel(r'$\\alpha$ coefficient')"
                },
                {
                    "command": "plt.legend(loc, fontsize, framealpha)",
                    "description": "Displays a legend for labeled plot elements.",
                    "example": "plt.legend(loc='upper right', fontsize=10, framealpha=0.8)",
                    "tip": "loc='best' lets matplotlib pick optimal placement."
                },
                {
                    "command": "ax.annotate(text, xy, xytext, arrowprops)",
                    "description": "Adds an annotation with optional arrow pointing to xy from xytext.",
                    "example": "ax.annotate('Peak', xy=(3.14, 1), xytext=(4, 1.3), arrowprops=dict(arrowstyle='->'))",
                    "tip": "Essential for highlighting specific data points in publications."
                },
                {
                    "command": "ax.text(x, y, s, fontsize, ha, va)",
                    "description": "Places text at data coordinates (x, y).",
                    "example": "ax.text(0.5, 0.5, 'Center', ha='center', va='center', transform=ax.transAxes)",
                    "tip": "Use transform=ax.transAxes for axes-relative coordinates (0-1)."
                }
            ]
        },
        {
            "name": "Styling & Configuration",
            "commands": [
                {
                    "command": "plt.grid(visible, alpha, linestyle)",
                    "description": "Toggles grid lines on the current axes.",
                    "example": "plt.grid(True, alpha=0.3, linestyle='--')",
                    "tip": "Subtle grids (alpha=0.3) improve readability without clutter."
                },
                {
                    "command": "plt.xlim(left, right) / plt.ylim(bottom, top)",
                    "description": "Sets the display range for x/y axes.",
                    "example": "plt.xlim(0, 256); plt.ylim(0, 5000)",
                    "tip": "Useful for zooming into specific regions of interest."
                },
                {
                    "command": "plt.style.use(style)",
                    "description": "Applies a predefined visual style to all subsequent plots.",
                    "example": "plt.style.use('seaborn-v0_8-whitegrid')",
                    "tip": "Available styles: 'ggplot', 'seaborn', 'dark_background', 'bmh', etc."
                },
                {
                    "command": "plt.savefig(fname, dpi, bbox_inches, transparent)",
                    "description": "Saves the current figure to a file (PNG, PDF, SVG, etc.).",
                    "example": "plt.savefig('output.png', dpi=300, bbox_inches='tight')",
                    "tip": "bbox_inches='tight' removes whitespace. Use before plt.show()."
                }
            ]
        },
        {
            "name": "Output & Display",
            "commands": [
                {
                    "command": "plt.show()",
                    "description": "Renders and displays all open figures. In notebooks, triggers inline display.",
                    "example": "plt.show()",
                    "tip": "In scripts, this blocks execution until the window is closed."
                },
                {
                    "command": "plt.close(fig)",
                    "description": "Closes a figure window and frees memory. 'all' closes everything.",
                    "example": "plt.close('all')",
                    "tip": "Always close figures in loops to prevent memory leaks."
                }
            ]
        }
    ]
}


# ---------------------------------------------------------------------------
# Educational feature functions
# ---------------------------------------------------------------------------

def get_pixel_region(filename, x, y, size=10):
    """
    Return pixel values for a square region around (x, y).

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    x, y : int
        Centre column (x) and row (y) of the region.
    size : int
        Half-side length of the square region (actual side = 2*size + 1).

    Returns
    -------
    dict with pixel_grid (2D list of ints), width, height, and region_info.
    """
    img = load_image(filename)
    if img is None:
        return None

    h, w = img.shape
    x = max(0, min(x, w - 1))
    y = max(0, min(y, h - 1))

    y_start = max(0, y - size)
    y_end = min(h, y + size + 1)
    x_start = max(0, x - size)
    x_end = min(w, x + size + 1)

    region = img[y_start:y_end, x_start:x_end]
    pixel_grid = region.astype(int).tolist()

    return {
        "pixel_grid": pixel_grid,
        "width": w,
        "height": h,
        "region_info": {
            "center_x": x,
            "center_y": y,
            "x_start": x_start,
            "x_end": x_end - 1,
            "y_start": y_start,
            "y_end": y_end - 1,
            "region_width": x_end - x_start,
            "region_height": y_end - y_start,
            "center_value": int(img[y, x]),
        },
    }


def get_step_by_step_pipeline(filename1, filename2):
    """
    Return a comprehensive dict showing every step of the spatial
    difference process with explanations and representative code.

    Parameters
    ----------
    filename1, filename2 : str
        Image filenames inside IMAGES_DIR.

    Returns
    -------
    dict with a ``steps`` list.  Each step contains *what_happened*,
    *code*, and *data*.
    """
    path1 = IMAGES_DIR / filename1
    path2 = IMAGES_DIR / filename2
    if not path1.exists() or not path2.exists():
        return None

    steps = []

    # ------------------------------------------------------------------
    # Step 1 – Raw file info
    # ------------------------------------------------------------------
    step1_data = {
        "image1": {
            "path": str(path1),
            "size_bytes": path1.stat().st_size,
            "size_kb": round(path1.stat().st_size / 1024, 2),
            "format": path1.suffix,
        },
        "image2": {
            "path": str(path2),
            "size_bytes": path2.stat().st_size,
            "size_kb": round(path2.stat().st_size / 1024, 2),
            "format": path2.suffix,
        },
    }
    steps.append({
        "step": 1,
        "title": "Raw File Information",
        "what_happened": (
            "We start by inspecting the raw files on disk. The file size, "
            "path, and format tell us what we are working with before any "
            "pixel data is loaded into memory."
        ),
        "code": (
            "from pathlib import Path\n"
            "path1 = Path(filename1)\n"
            "path2 = Path(filename2)\n"
            "print(path1.stat().st_size)  # size in bytes\n"
            "print(path1.suffix)          # file extension"
        ),
        "data": step1_data,
    })

    # ------------------------------------------------------------------
    # Step 2 – After imread
    # ------------------------------------------------------------------
    img1 = cv2.imread(str(path1), cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(str(path2), cv2.IMREAD_GRAYSCALE)
    if img1 is None or img2 is None:
        return None

    def _sample_5x5(img):
        """Extract a 5x5 sample from the centre of an image."""
        cy, cx = img.shape[0] // 2, img.shape[1] // 2
        return img[cy - 2:cy + 3, cx - 2:cx + 3].astype(int).tolist()

    step2_data = {
        "image1": {
            "shape": list(img1.shape),
            "dtype": str(img1.dtype),
            "min": int(img1.min()),
            "max": int(img1.max()),
            "sample_5x5_center": _sample_5x5(img1),
        },
        "image2": {
            "shape": list(img2.shape),
            "dtype": str(img2.dtype),
            "min": int(img2.min()),
            "max": int(img2.max()),
            "sample_5x5_center": _sample_5x5(img2),
        },
    }
    steps.append({
        "step": 2,
        "title": "After cv2.imread()",
        "what_happened": (
            "cv2.imread with IMREAD_GRAYSCALE loads the file into a 2-D "
            "NumPy array of dtype uint8 (values 0-255). We inspect the "
            "shape, data type, and a 5x5 sample from the centre so we "
            "can verify the data looks reasonable."
        ),
        "code": (
            "import cv2\n"
            "img1 = cv2.imread(path1, cv2.IMREAD_GRAYSCALE)\n"
            "img2 = cv2.imread(path2, cv2.IMREAD_GRAYSCALE)\n"
            "print(img1.shape, img1.dtype, img1.min(), img1.max())"
        ),
        "data": step2_data,
    })

    # ------------------------------------------------------------------
    # Step 3 – Resize check
    # ------------------------------------------------------------------
    resized = False
    original_shape2 = list(img2.shape)
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]),
                          interpolation=cv2.INTER_AREA)
        resized = True

    step3_data = {
        "resized": resized,
        "image1_shape": list(img1.shape),
        "image2_original_shape": original_shape2,
        "image2_final_shape": list(img2.shape),
    }
    steps.append({
        "step": 3,
        "title": "Resize Check",
        "what_happened": (
            "Image subtraction requires both arrays to have the same "
            "dimensions. If they differ, we resize image 2 to match image 1 "
            "using INTER_AREA interpolation (good for downsampling)."
            + (" Images had different sizes and were resized." if resized
               else " Images already matched -- no resize needed.")
        ),
        "code": (
            "if img1.shape != img2.shape:\n"
            "    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]),\n"
            "                      interpolation=cv2.INTER_AREA)"
        ),
        "data": step3_data,
    })

    # ------------------------------------------------------------------
    # Step 4 – The subtraction
    # ------------------------------------------------------------------
    diff = cv2.absdiff(img1, img2)

    def _sample_region(img, label=""):
        cy, cx = img.shape[0] // 2, img.shape[1] // 2
        return img[cy - 2:cy + 3, cx - 2:cx + 3].astype(int).tolist()

    step4_data = {
        "sample_img1_5x5": _sample_region(img1),
        "sample_img2_5x5": _sample_region(img2),
        "sample_diff_5x5": _sample_region(diff),
        "explanation": (
            "Each value in the difference grid equals |img1 - img2| at "
            "that pixel. For example, if img1 pixel is 120 and img2 is 95, "
            "the difference is |120 - 95| = 25."
        ),
    }
    steps.append({
        "step": 4,
        "title": "Absolute Subtraction",
        "what_happened": (
            "cv2.absdiff computes the per-pixel absolute difference. Unlike "
            "simple subtraction (which wraps around for uint8), absdiff "
            "always produces the true magnitude |a - b|. The sample grids "
            "let you verify the arithmetic by hand."
        ),
        "code": (
            "import cv2\n"
            "diff = cv2.absdiff(img1, img2)\n"
            "# Equivalent to: np.abs(img1.astype(int) - img2.astype(int)).astype(np.uint8)"
        ),
        "data": step4_data,
    })

    # ------------------------------------------------------------------
    # Step 5 – Statistics
    # ------------------------------------------------------------------
    stats = {
        "mean_difference": round(float(np.mean(diff)), 4),
        "max_difference": int(np.max(diff)),
        "min_difference": int(np.min(diff)),
        "std_difference": round(float(np.std(diff)), 4),
        "nonzero_pixels": int(np.count_nonzero(diff)),
        "total_pixels": int(diff.size),
        "nonzero_percentage": round(
            float(np.count_nonzero(diff)) / diff.size * 100, 2
        ),
    }
    steps.append({
        "step": 5,
        "title": "Compute Statistics",
        "what_happened": (
            "Summary statistics quantify how different the two images are. "
            "Mean difference tells overall brightness shift, std tells "
            "variability, and nonzero percentage tells what fraction of "
            "the image actually changed."
        ),
        "code": (
            "import numpy as np\n"
            "mean_diff = np.mean(diff)\n"
            "max_diff  = np.max(diff)\n"
            "std_diff  = np.std(diff)\n"
            "nonzero   = np.count_nonzero(diff)"
        ),
        "data": stats,
    })

    # ------------------------------------------------------------------
    # Step 6 – Normalization / enhancement
    # ------------------------------------------------------------------
    if diff.max() > 0:
        diff_enhanced = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    else:
        diff_enhanced = diff.copy()

    step6_data = {
        "original_range": [int(diff.min()), int(diff.max())],
        "enhanced_range": [int(diff_enhanced.min()), int(diff_enhanced.max())],
        "diff_image": image_to_base64_png(diff),
        "enhanced_image": image_to_base64_png(diff_enhanced),
    }
    steps.append({
        "step": 6,
        "title": "Normalization / Enhancement",
        "what_happened": (
            "The raw difference image often uses only a small part of the "
            "0-255 range, making it look very dark. cv2.normalize stretches "
            "the values to span the full range, making subtle differences "
            "visible. Original range [{0}, {1}] is mapped to [0, 255].".format(
                int(diff.min()), int(diff.max())
            )
        ),
        "code": (
            "diff_enhanced = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)\n"
            "# Maps [min, max] -> [0, 255] linearly"
        ),
        "data": step6_data,
    })

    return {"steps": steps}


def generate_surface_plot(filename, region_x=0, region_y=0, region_size=64):
    """
    Generate a 3-D surface plot of pixel intensities for a region.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.
    region_x, region_y : int
        Top-left corner of the region (column, row).
    region_size : int
        Side length of the square region (capped at 128 for performance).

    Returns
    -------
    Base64-encoded PNG string, or None on failure.
    """
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 -- registers '3d' projection

    img = load_image(filename)
    if img is None:
        return None

    h, w = img.shape
    region_size = min(region_size, 128)  # cap for performance

    # Clamp region to image bounds
    x_start = max(0, min(region_x, w - 1))
    y_start = max(0, min(region_y, h - 1))
    x_end = min(w, x_start + region_size)
    y_end = min(h, y_start + region_size)

    region = img[y_start:y_end, x_start:x_end].astype(np.float64)

    # Build coordinate grids
    X = np.arange(x_start, x_end)
    Y = np.arange(y_start, y_end)
    X, Y = np.meshgrid(X, Y)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot_surface(X, Y, region, cmap='viridis', edgecolor='none',
                    alpha=0.9, rstride=1, cstride=1)

    ax.set_xlabel('X (column)')
    ax.set_ylabel('Y (row)')
    ax.set_zlabel('Intensity')
    ax.set_title(
        f'3-D Surface Plot  —  Region ({x_start},{y_start}) to '
        f'({x_end-1},{y_end-1})',
        fontsize=11, fontweight='bold',
    )
    ax.view_init(elev=35, azim=225)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def compute_pixel_arithmetic(val1, val2):
    """
    Demonstrate all arithmetic operations on two uint8 pixel values.

    Parameters
    ----------
    val1, val2 : int
        Pixel values in [0, 255].

    Returns
    -------
    dict with operation results and educational explanations.
    """
    v1 = np.uint8(max(0, min(255, int(val1))))
    v2 = np.uint8(max(0, min(255, int(val2))))

    # --- Addition ---
    # Intentional overflow to demonstrate uint8 wrapping behaviour
    with np.errstate(over='ignore'):
        add_overflow = int(np.uint8(v1) + np.uint8(v2))   # wraps at 256
    add_correct = int(min(int(v1) + int(v2), 255))         # saturated

    # --- Simple subtraction ---
    # We compute the wrap explicitly via modular arithmetic
    raw_sub = int(v1) - int(v2)
    sub_underflow = raw_sub % 256  # uint8 wrap behaviour

    # --- Absolute difference ---
    absdiff_val = int(abs(int(v1) - int(v2)))

    # --- Multiplication (scaled by 1/255 to keep in range) ---
    mul_raw = int(v1) * int(v2)
    mul_scaled = int(round(mul_raw / 255.0))

    # --- Division ---
    if int(v2) == 0:
        div_result = 255  # convention: saturate to max on divide-by-zero
        div_note = "Division by zero -- result saturated to 255."
    else:
        div_result = int(round(int(v1) / int(v2)))
        div_result = min(div_result, 255)
        div_note = f"{int(v1)} / {int(v2)} = {int(v1)/int(v2):.4f}, rounded to {div_result}."

    return {
        "val1": int(v1),
        "val2": int(v2),
        "operations": {
            "addition": {
                "with_overflow": add_overflow,
                "saturated": add_correct,
                "explanation": (
                    f"uint8 addition: {int(v1)} + {int(v2)} = {int(v1)+int(v2)}. "
                    f"With overflow wrap (mod 256) the result is {add_overflow}. "
                    f"Saturated (clamped to 255) the result is {add_correct}. "
                    "OpenCV's cv2.add() uses saturation arithmetic."
                ),
            },
            "subtraction": {
                "with_underflow": sub_underflow,
                "explanation": (
                    f"uint8 subtraction: {int(v1)} - {int(v2)} = {raw_sub}. "
                    f"With underflow wrap (mod 256) the result is {sub_underflow}. "
                    "Negative results wrap around: e.g. -1 becomes 255. "
                    "This is why simple subtraction is dangerous for images."
                ),
            },
            "absdiff": {
                "result": absdiff_val,
                "explanation": (
                    f"|{int(v1)} - {int(v2)}| = {absdiff_val}. "
                    "cv2.absdiff() always returns the true magnitude of the "
                    "difference, avoiding uint8 underflow. This is the correct "
                    "way to compute pixel-wise differences."
                ),
            },
            "multiplication": {
                "raw": mul_raw,
                "scaled": mul_scaled,
                "explanation": (
                    f"{int(v1)} * {int(v2)} = {mul_raw}. Raw product can be up to "
                    f"255*255 = 65025, far exceeding uint8 range. "
                    f"Scaled (raw / 255) gives {mul_scaled}, keeping the "
                    "result in [0, 255]. This scaling models 'blending' or 'masking'."
                ),
            },
            "division": {
                "result": div_result,
                "explanation": div_note + (
                    " Division is used in shading correction: corrected = image / shading_pattern. "
                    "Always guard against divide-by-zero."
                ),
            },
        },
    }


def generate_bit_depth_comparison(filename):
    """
    Show the same image quantised to 8, 4, 2, and 1 bit depths,
    each accompanied by its histogram.

    Parameters
    ----------
    filename : str
        Image filename inside IMAGES_DIR.

    Returns
    -------
    dict mapping bit-depth labels to base64 PNG strings (image + histogram).
    Returns None on failure.
    """
    img = load_image(filename)
    if img is None:
        return None

    results = {}
    bit_depths = [8, 4, 2, 1]

    for bits in bit_depths:
        levels = 2 ** bits  # number of quantisation levels
        if bits == 8:
            quantised = img.copy()
        else:
            # Quantise: divide into `levels` bins, then scale back to 0-255
            step = 256 // levels
            quantised = (img // step) * step
            # Map to full 0-255 for display
            quantised = cv2.normalize(quantised, None, 0, 255,
                                      cv2.NORM_MINMAX).astype(np.uint8)

        # Build a figure with the image and its histogram side by side
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))

        axes[0].imshow(quantised, cmap='gray', vmin=0, vmax=255)
        axes[0].set_title(f'{bits}-bit  ({levels} levels)', fontsize=11,
                          fontweight='bold')
        axes[0].axis('off')

        hist = cv2.calcHist([quantised], [0], None, [256], [0, 256])
        axes[1].bar(range(256), hist.flatten(), color='#3498db', width=1.0,
                    edgecolor='none')
        axes[1].set_xlim([0, 256])
        axes[1].set_xlabel('Pixel Intensity')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title(f'Histogram  ({bits}-bit)', fontsize=11)
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=120, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)
        results[f"{bits}_bit"] = base64.b64encode(buf.read()).decode('utf-8')

    return results
