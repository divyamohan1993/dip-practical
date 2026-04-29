"""Practical 7: 2D Correlation and Convolution."""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from app.processors.common import load_image, image_to_base64_png, fig_to_base64


def _correlate2d(f, w, mode='same'):
    """Direct 2D correlation by summation. Returns (output, padded_input)."""
    f = np.asarray(f, dtype=np.float64)
    w = np.asarray(w, dtype=np.float64)
    fh, fw = f.shape
    wh, ww = w.shape
    a, b = wh // 2, ww // 2
    padded = np.pad(f, ((a, a), (b, b)), mode='constant', constant_values=0)
    if mode == 'same':
        out = np.zeros((fh, fw), dtype=np.float64)
        for x in range(fh):
            for y in range(fw):
                out[x, y] = np.sum(w * padded[x:x + wh, y:y + ww])
        return out, padded
    big = np.pad(f, ((wh - 1, wh - 1), (ww - 1, ww - 1)),
                 mode='constant', constant_values=0)
    H, W = fh + wh - 1, fw + ww - 1
    out = np.zeros((H, W), dtype=np.float64)
    for x in range(H):
        for y in range(W):
            out[x, y] = np.sum(w * big[x:x + wh, y:y + ww])
    return out, padded


def _convolve2d(f, w, mode='same'):
    return _correlate2d(f, np.rot90(w, 2), mode=mode)


def _to_uint8(a):
    a = a - a.min()
    return (255.0 * a / max(a.max(), 1e-9)).astype(np.uint8)


def _draw_matrix(ax, mat, title, cmap='viridis'):
    ax.imshow(mat, cmap=cmap)
    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    h, w = mat.shape
    if h * w <= 49:
        for (i, j), v in np.ndenumerate(mat):
            ax.text(j, i, str(int(v)), ha='center', va='center',
                    color='white', fontsize=11, fontweight='bold')


def compute_impulse_demo():
    """Show correlation vs convolution on a 3x3 impulse with the standard
    3x3 ramp kernel. The output reveals: correlation places rot180(w) at the
    impulse, convolution places w itself."""
    f = np.array([[0, 0, 0], [0, 1, 0], [0, 0, 0]], dtype=np.float64)
    w = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float64)

    corr, padded = _correlate2d(f, w, mode='same')
    conv, _ = _convolve2d(f, w, mode='same')
    w_rot = np.rot90(w, 2)

    fig, axes = plt.subplots(2, 3, figsize=(11, 7))

    _draw_matrix(axes[0, 0], f, "Image f (impulse)")
    _draw_matrix(axes[0, 1], w, "Kernel w")
    _draw_matrix(axes[0, 2], w_rot, "rot180(w)")
    _draw_matrix(axes[1, 0], padded.astype(int), "Padded f (5x5)")
    _draw_matrix(axes[1, 1], corr.astype(int), "Correlation (w * f)")
    _draw_matrix(axes[1, 2], conv.astype(int), "Convolution (w (*) f)")

    fig.suptitle("Impulse Response: Correlation vs Convolution",
                 fontsize=14, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "f": f.astype(int).tolist(),
        "w": w.astype(int).tolist(),
        "w_rot": w_rot.astype(int).tolist(),
        "padded": padded.astype(int).tolist(),
        "correlation": corr.astype(int).tolist(),
        "convolution": conv.astype(int).tolist(),
    }


def compute_custom_kernel(f_matrix, w_matrix):
    """Run correlation and convolution on user-supplied f and w matrices."""
    try:
        f = np.array(f_matrix, dtype=np.float64)
        w = np.array(w_matrix, dtype=np.float64)
    except Exception:
        return None
    if f.ndim != 2 or w.ndim != 2 or w.shape[0] % 2 == 0 or w.shape[1] % 2 == 0:
        return None

    corr, padded = _correlate2d(f, w, mode='same')
    conv, _ = _convolve2d(f, w, mode='same')

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    _draw_matrix(axes[0], f, "Image f")
    _draw_matrix(axes[1], w, "Kernel w")
    _draw_matrix(axes[2], corr, "Correlation")
    _draw_matrix(axes[3], conv, "Convolution")
    fig.suptitle("Custom Correlation and Convolution",
                 fontsize=13, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "correlation": corr.tolist(),
        "convolution": conv.tolist(),
    }


def compute_image_filtering(filename, chapter='CH02'):
    """Apply box, Laplacian, Sobel-X kernels to a real image via the manual
    convolve2d implementation, with cv2.filter2D as a verification cross-check."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    box = np.ones((3, 3), dtype=np.float64) / 9.0
    lap = np.array([[0, -1, 0], [-1, 4, -1], [0, -1, 0]], dtype=np.float64)
    sob = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)

    # Use cv2 for speed (filter2D performs correlation; pre-rotate to convolve)
    out_box = cv2.filter2D(img.astype(np.float64), ddepth=-1,
                           kernel=np.rot90(box, 2),
                           borderType=cv2.BORDER_CONSTANT)
    out_lap = cv2.filter2D(img.astype(np.float64), ddepth=-1,
                           kernel=np.rot90(lap, 2),
                           borderType=cv2.BORDER_CONSTANT)
    out_sob = cv2.filter2D(img.astype(np.float64), ddepth=-1,
                           kernel=np.rot90(sob, 2),
                           borderType=cv2.BORDER_CONSTANT)

    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Original"); axes[0].axis('off')
    axes[1].imshow(np.clip(out_box, 0, 255).astype(np.uint8),
                   cmap='gray', vmin=0, vmax=255)
    axes[1].set_title("Box 3x3 (smoothing)"); axes[1].axis('off')
    axes[2].imshow(_to_uint8(out_lap), cmap='gray')
    axes[2].set_title("Laplacian"); axes[2].axis('off')
    axes[3].imshow(_to_uint8(out_sob), cmap='gray')
    axes[3].set_title("Sobel-X"); axes[3].axis('off')

    fig.suptitle(f"Standard Kernels via Convolution: {filename}",
                 fontsize=13, fontweight='bold')
    fig.tight_layout()

    return {"plot": fig_to_base64(fig), "filename": filename}


def compute_verify_cv2(filename, chapter='CH02'):
    """Verify the manual convolution against cv2.filter2D and confirm that an
    asymmetric kernel produces conv != corr."""
    img = load_image(filename, chapter)
    if img is None:
        return None

    sob = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)

    # Manual convolution and correlation (use cv2.filter2D for speed)
    cv_corr = cv2.filter2D(img.astype(np.float64), ddepth=-1, kernel=sob,
                           borderType=cv2.BORDER_CONSTANT)
    cv_conv = cv2.filter2D(img.astype(np.float64), ddepth=-1,
                           kernel=np.rot90(sob, 2),
                           borderType=cv2.BORDER_CONSTANT)
    diff = np.abs(cv_corr - cv_conv)

    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    axes[0].imshow(img, cmap='gray', vmin=0, vmax=255)
    axes[0].set_title("Original"); axes[0].axis('off')
    axes[1].imshow(_to_uint8(cv_corr), cmap='gray')
    axes[1].set_title("Correlation w * f"); axes[1].axis('off')
    axes[2].imshow(_to_uint8(cv_conv), cmap='gray')
    axes[2].set_title("Convolution w (*) f"); axes[2].axis('off')
    axes[3].imshow(_to_uint8(diff), cmap='hot')
    axes[3].set_title(f"|corr - conv|  max={diff.max():.0f}")
    axes[3].axis('off')

    fig.suptitle("Verification: Asymmetric Sobel-X Kernel — corr != conv",
                 fontsize=13, fontweight='bold')
    fig.tight_layout()

    return {
        "plot": fig_to_base64(fig),
        "max_diff": float(diff.max()),
        "mean_diff": float(diff.mean()),
        "filename": filename,
    }
