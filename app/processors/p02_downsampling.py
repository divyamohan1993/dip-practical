"""Practical 2: Impact of Sampling Rate on Spatial Resolution (Downsampling)."""
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


def downsample_series(filename, chapter='CH02', steps=5):
    """Progressively downsample an image by factor of 2 for given steps."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    baseline = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_LINEAR)

    results = []
    current = baseline.copy()
    results.append({
        "image": image_to_base64_png(current),
        "label": "1024x1024",
        "width": 1024,
        "height": 1024,
    })

    for i in range(steps):
        h, w = current.shape
        new_h, new_w = h // 2, w // 2
        if new_h < 1 or new_w < 1:
            break
        current = cv2.resize(current, (new_w, new_h), interpolation=cv2.INTER_AREA)
        results.append({
            "image": image_to_base64_png(current),
            "label": f"{new_w}x{new_h}",
            "width": new_w,
            "height": new_h,
        })

    return {"steps": results, "filename": filename}


def downsample_comparison_plot(filename, chapter='CH02', steps=5):
    """Generate a 2x3 comparison plot of all downsample levels."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    baseline = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_LINEAR)

    images = [baseline]
    labels = ["1024x1024"]
    current = baseline.copy()

    for i in range(steps):
        h, w = current.shape
        new_h, new_w = h // 2, w // 2
        if new_h < 1 or new_w < 1:
            break
        current = cv2.resize(current, (new_w, new_h), interpolation=cv2.INTER_AREA)
        images.append(current)
        labels.append(f"{new_w}x{new_h}")

    n = len(images)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()

    for ax, im, label in zip(axes, images, labels):
        ax.imshow(im, cmap='gray')
        ax.set_title(label, fontsize=12, fontweight='bold')
        ax.axis('off')

    for j in range(n, len(axes)):
        axes[j].axis('off')

    fig.suptitle(f"Progressive Downsampling: {filename}", fontsize=14, fontweight='bold')
    fig.tight_layout()
    return {"plot": fig_to_base64(fig)}


def upscale_comparison_plot(filename, chapter='CH02', steps=5):
    """Downsample then upscale back to 1024x1024 to show quality loss."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    baseline = cv2.resize(img, (1024, 1024), interpolation=cv2.INTER_LINEAR)

    images = [baseline]
    labels = ["1024x1024\n(Original)"]
    current = baseline.copy()

    for i in range(steps):
        h, w = current.shape
        new_h, new_w = h // 2, w // 2
        if new_h < 1 or new_w < 1:
            break
        current = cv2.resize(current, (new_w, new_h), interpolation=cv2.INTER_AREA)
        upscaled = cv2.resize(current, (1024, 1024), interpolation=cv2.INTER_LINEAR)
        images.append(upscaled)
        labels.append(f"From {new_w}x{new_h}")

    n = len(images)
    cols = 3
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()

    for ax, im, label in zip(axes, images, labels):
        ax.imshow(im, cmap='gray')
        ax.set_title(label, fontsize=11)
        ax.axis('off')

    for j in range(n, len(axes)):
        axes[j].axis('off')

    fig.suptitle("Quality Loss: Downsampled then Upscaled to 1024x1024", fontsize=14, fontweight='bold')
    fig.tight_layout()
    return {"plot": fig_to_base64(fig)}
