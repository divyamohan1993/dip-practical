"""Practical 4: Gamma Correction and Power Law Transformations."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


def apply_gamma(filename, gamma=1.0, c=1.0):
    """Apply gamma correction: s = c * r^gamma. Returns original + corrected + histogram comparison."""
    img = load_image(filename)
    if img is None:
        return None

    # Normalize to [0, 1], apply gamma, convert back
    normalized = img / 255.0
    corrected = c * np.power(normalized, gamma)
    corrected_uint8 = np.uint8(np.clip(corrected * 255, 0, 255))

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    axes[0, 0].imshow(img, cmap='gray')
    axes[0, 0].set_title("Original")
    axes[0, 0].axis('off')

    axes[0, 1].imshow(corrected_uint8, cmap='gray')
    axes[0, 1].set_title(f"Gamma Corrected (γ={gamma}, c={c})")
    axes[0, 1].axis('off')

    axes[1, 0].hist(img.ravel(), bins=256, range=(0, 256), color='black', alpha=0.7)
    axes[1, 0].set_title("Original Histogram")
    axes[1, 0].set_xlabel("Intensity")
    axes[1, 0].set_ylabel("Frequency")

    axes[1, 1].hist(corrected_uint8.ravel(), bins=256, range=(0, 256), color='black', alpha=0.7)
    axes[1, 1].set_title(f"Corrected Histogram (γ={gamma})")
    axes[1, 1].set_xlabel("Intensity")
    axes[1, 1].set_ylabel("Frequency")

    fig.suptitle(f"Gamma Correction: {filename}", fontsize=13, fontweight='bold')
    fig.tight_layout()

    return {
        "original": image_to_base64_png(img),
        "corrected": image_to_base64_png(corrected_uint8),
        "plot": fig_to_base64(fig),
        "filename": filename,
        "gamma": gamma,
        "c": c,
    }


def gamma_series(filename, gammas=None):
    """Apply multiple gamma values and show comparison grid."""
    if gammas is None:
        gammas = [0.3, 0.5, 1.0, 1.5, 2.5, 5.0]

    img = load_image(filename)
    if img is None:
        return None

    normalized = img / 255.0
    n = len(gammas)
    cols = 3
    rows = (n + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()

    for ax, gamma in zip(axes, gammas):
        corrected = np.uint8(np.clip(np.power(normalized, gamma) * 255, 0, 255))
        ax.imshow(corrected, cmap='gray')
        ax.set_title(f"γ = {gamma}", fontsize=13, fontweight='bold')
        ax.axis('off')

    for j in range(n, len(axes)):
        axes[j].axis('off')

    fig.suptitle(f"Gamma Correction Series: s = c · r^γ", fontsize=15, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "gammas": gammas}


def log_transform(filename):
    """Apply log transformation: s = c * log(1 + r). Compare with gamma=0.4."""
    img = load_image(filename)
    if img is None:
        return None

    normalized = img / 255.0

    # Log transform
    log_result = np.log1p(normalized)
    log_result = log_result / log_result.max()  # normalize to [0, 1]
    log_uint8 = np.uint8(log_result * 255)

    # Gamma 0.4 for comparison
    gamma_result = np.uint8(np.clip(np.power(normalized, 0.4) * 255, 0, 255))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img, cmap='gray')
    axes[0].set_title("Original")
    axes[0].axis('off')

    axes[1].imshow(log_uint8, cmap='gray')
    axes[1].set_title("Log: s = c·log(1+r)")
    axes[1].axis('off')

    axes[2].imshow(gamma_result, cmap='gray')
    axes[2].set_title("Gamma: s = r^0.4")
    axes[2].axis('off')

    fig.suptitle("Log Transformation vs Gamma Correction", fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "original": image_to_base64_png(img),
        "log_transformed": image_to_base64_png(log_uint8),
        "gamma_result": image_to_base64_png(gamma_result),
        "plot": fig_to_base64(fig),
    }


def transformation_curves():
    """Generate plot of gamma transformation curves for different gamma values."""
    r = np.linspace(0, 1, 256)
    gammas = [0.04, 0.1, 0.2, 0.4, 0.67, 1.0, 1.5, 2.5, 5.0, 10.0, 25.0]

    fig, ax = plt.subplots(figsize=(8, 8))
    for gamma in gammas:
        s = np.power(r, gamma)
        ax.plot(r, s, label=f"γ = {gamma}")

    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label="Identity (γ=1)")
    ax.set_xlabel("Input Intensity (r)", fontsize=12)
    ax.set_ylabel("Output Intensity (s)", fontsize=12)
    ax.set_title("Power Law Transformation Curves: s = r^γ", fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig)}


def contrast_enhancement(filename, gammas=None, mode="dark"):
    """Enhance dark images (gamma<1) or compress bright images (gamma>1)."""
    if gammas is None:
        gammas = [0.3, 0.4, 0.6] if mode == "dark" else [3.0, 4.0, 5.0]

    img = load_image(filename)
    if img is None:
        return None

    normalized = img / 255.0
    n = len(gammas) + 1  # +1 for original

    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))

    axes[0].imshow(img, cmap='gray')
    axes[0].set_title(f"Original ({'Dark' if mode == 'dark' else 'Bright'})")
    axes[0].axis('off')

    for i, gamma in enumerate(gammas):
        enhanced = np.uint8(np.clip(np.power(normalized, gamma) * 255, 0, 255))
        axes[i + 1].imshow(enhanced, cmap='gray')
        axes[i + 1].set_title(f"γ = {gamma}")
        axes[i + 1].axis('off')

    label = "Dark Image Enhancement" if mode == "dark" else "Bright Image Compression"
    fig.suptitle(label, fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "mode": mode, "gammas": gammas}
