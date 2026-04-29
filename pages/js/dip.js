/**
 * DIP Practical - Client-Side Image Processing (Static Edition)
 * All image operations run entirely in the browser using Canvas API.
 */
(function () {
    'use strict';
    window.DIP = window.DIP || {};

    // ---- Load PNG image and extract grayscale channel ----
    DIP.loadImage = function(url) {
        return new Promise(function(resolve, reject) {
            var img = new Image();
            img.crossOrigin = 'anonymous';
            img.onload = function() {
                var c = document.createElement('canvas');
                c.width = img.width;
                c.height = img.height;
                var ctx = c.getContext('2d');
                ctx.drawImage(img, 0, 0);
                var data = ctx.getImageData(0, 0, img.width, img.height).data;
                var gray = new Uint8Array(img.width * img.height);
                for (var i = 0; i < gray.length; i++) {
                    // Luminance: 0.299R + 0.587G + 0.114B
                    var j = i * 4;
                    gray[i] = Math.round(0.299 * data[j] + 0.587 * data[j+1] + 0.114 * data[j+2]);
                }
                resolve({ gray: gray, width: img.width, height: img.height });
            };
            img.onerror = function() { reject(new Error('Failed to load: ' + url)); };
            img.src = url;
        });
    };

    // ---- Compute histogram (256 bins) ----
    DIP.histogram = function(gray) {
        var hist = new Uint32Array(256);
        for (var i = 0; i < gray.length; i++) hist[gray[i]]++;
        return hist;
    };

    // ---- Compute PDF (normalized histogram) ----
    DIP.pdf = function(hist) {
        var total = 0;
        for (var i = 0; i < 256; i++) total += hist[i];
        var pdf = new Float64Array(256);
        if (total === 0) return pdf;
        for (var i = 0; i < 256; i++) pdf[i] = hist[i] / total;
        return pdf;
    };

    // ---- Compute CDF ----
    DIP.cdf = function(pdf) {
        var cdf = new Float64Array(256);
        cdf[0] = pdf[0];
        for (var i = 1; i < 256; i++) cdf[i] = cdf[i-1] + pdf[i];
        return cdf;
    };

    // ---- Histogram equalization ----
    DIP.equalize = function(gray) {
        var hist = DIP.histogram(gray);
        var pdf = DIP.pdf(hist);
        var cdf = DIP.cdf(pdf);
        var lut = new Uint8Array(256);
        for (var i = 0; i < 256; i++) lut[i] = Math.round(cdf[i] * 255);
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) out[i] = lut[gray[i]];
        return out;
    };

    // ---- Image negation: s = 255 - r ----
    DIP.negate = function(gray) {
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) out[i] = 255 - gray[i];
        return out;
    };

    // ---- Gamma correction: s = c * r^gamma ----
    DIP.gamma = function(gray, gamma, c) {
        if (typeof c === 'undefined') c = 1.0;
        var lut = new Uint8Array(256);
        for (var i = 0; i < 256; i++) {
            lut[i] = DIP.clamp255(c * Math.pow(i / 255, gamma) * 255);
        }
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) out[i] = lut[gray[i]];
        return out;
    };

    // ---- Log transform: s = c * log(1 + r) ----
    DIP.logTransform = function(gray) {
        var maxLog = Math.log(1 + 255);
        var lut = new Uint8Array(256);
        for (var i = 0; i < 256; i++) {
            lut[i] = DIP.clamp255((Math.log(1 + i) / maxLog) * 255);
        }
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) out[i] = lut[gray[i]];
        return out;
    };

    // ---- Absolute difference: |img1 - img2| ----
    DIP.subtract = function(gray1, gray2) {
        var len = Math.min(gray1.length, gray2.length);
        var out = new Uint8Array(len);
        for (var i = 0; i < len; i++) out[i] = Math.abs(gray1[i] - gray2[i]);
        return out;
    };

    // ---- Contrast stretch to full 0-255 range ----
    DIP.contrastStretch = function(gray) {
        var lo = 255, hi = 0;
        for (var i = 0; i < gray.length; i++) {
            if (gray[i] < lo) lo = gray[i];
            if (gray[i] > hi) hi = gray[i];
        }
        if (hi === lo) return new Uint8Array(gray.length);
        var scale = 255 / (hi - lo);
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) out[i] = DIP.clamp255((gray[i] - lo) * scale);
        return out;
    };

    // ---- Downsample using area averaging ----
    DIP.downsample = function(gray, w, h, newW, newH) {
        var out = new Uint8Array(newW * newH);
        var scaleX = w / newW;
        var scaleY = h / newH;
        for (var y = 0; y < newH; y++) {
            for (var x = 0; x < newW; x++) {
                var sx0 = Math.floor(x * scaleX);
                var sy0 = Math.floor(y * scaleY);
                var sx1 = Math.min(Math.floor((x + 1) * scaleX), w);
                var sy1 = Math.min(Math.floor((y + 1) * scaleY), h);
                var sum = 0, count = 0;
                for (var sy = sy0; sy < sy1; sy++) {
                    for (var sx = sx0; sx < sx1; sx++) {
                        sum += gray[sy * w + sx];
                        count++;
                    }
                }
                out[y * newW + x] = count > 0 ? Math.round(sum / count) : 0;
            }
        }
        return { gray: out, width: newW, height: newH };
    };

    // ---- Upscale using bilinear interpolation ----
    DIP.upscale = function(gray, w, h, newW, newH) {
        var out = new Uint8Array(newW * newH);
        var scaleX = (w - 1) / (newW - 1);
        var scaleY = (h - 1) / (newH - 1);
        for (var y = 0; y < newH; y++) {
            for (var x = 0; x < newW; x++) {
                var srcX = x * scaleX;
                var srcY = y * scaleY;
                var x0 = Math.floor(srcX);
                var y0 = Math.floor(srcY);
                var x1 = Math.min(x0 + 1, w - 1);
                var y1 = Math.min(y0 + 1, h - 1);
                var fx = srcX - x0;
                var fy = srcY - y0;
                var v = (1-fx)*(1-fy)*gray[y0*w+x0] + fx*(1-fy)*gray[y0*w+x1]
                      + (1-fx)*fy*gray[y1*w+x0] + fx*fy*gray[y1*w+x1];
                out[y * newW + x] = DIP.clamp255(v);
            }
        }
        return { gray: out, width: newW, height: newH };
    };

    // ---- Compute statistics ----
    DIP.stats = function(gray) {
        var min = 255, max = 0, sum = 0;
        for (var i = 0; i < gray.length; i++) {
            if (gray[i] < min) min = gray[i];
            if (gray[i] > max) max = gray[i];
            sum += gray[i];
        }
        var mean = sum / gray.length;
        var sumSq = 0;
        for (var i = 0; i < gray.length; i++) {
            var d = gray[i] - mean;
            sumSq += d * d;
        }
        var std = Math.sqrt(sumSq / gray.length);
        return { min: min, max: max, mean: Math.round(mean * 100) / 100, std: Math.round(std * 100) / 100 };
    };

    // ---- Convert grayscale array to ImageData ----
    DIP.grayToImageData = function(gray, w, h) {
        var canvas = document.createElement('canvas');
        var ctx = canvas.getContext('2d');
        var id = ctx.createImageData(w, h);
        var d = id.data;
        for (var i = 0; i < gray.length; i++) {
            var v = gray[i], j = i * 4;
            d[j] = v; d[j+1] = v; d[j+2] = v; d[j+3] = 255;
        }
        return id;
    };

    // ============================================================
    // Practical 7: 2D Correlation and Convolution
    // ============================================================

    // ---- Pad a 2D array with zeros (a rows top/bot, b cols left/right) ----
    DIP.padZero = function(mat, a, b) {
        var h = mat.length, w = mat[0].length;
        var H = h + 2*a, W = w + 2*b;
        var out = [];
        for (var i = 0; i < H; i++) {
            var row = new Array(W);
            for (var j = 0; j < W; j++) row[j] = 0;
            out.push(row);
        }
        for (var i = 0; i < h; i++)
            for (var j = 0; j < w; j++)
                out[i + a][j + b] = mat[i][j];
        return out;
    };

    // ---- Rotate 2D array by 180 degrees ----
    DIP.rot180 = function(mat) {
        var h = mat.length, w = mat[0].length;
        var out = [];
        for (var i = 0; i < h; i++) {
            var row = new Array(w);
            for (var j = 0; j < w; j++) row[j] = mat[h - 1 - i][w - 1 - j];
            out.push(row);
        }
        return out;
    };

    // ---- 2D correlation on a 2D array with a small kernel ----
    DIP.correlate2dArray = function(f, w) {
        var fh = f.length, fw = f[0].length;
        var wh = w.length, ww = w[0].length;
        var a = (wh / 2) | 0, b = (ww / 2) | 0;
        var padded = DIP.padZero(f, a, b);
        var out = [];
        for (var x = 0; x < fh; x++) {
            var row = new Array(fw);
            for (var y = 0; y < fw; y++) {
                var s = 0;
                for (var i = 0; i < wh; i++)
                    for (var j = 0; j < ww; j++)
                        s += w[i][j] * padded[x + i][y + j];
                row[y] = s;
            }
            out.push(row);
        }
        return { out: out, padded: padded };
    };

    // ---- 2D convolution on a 2D array (= correlation with rot180(w)) ----
    DIP.convolve2dArray = function(f, w) {
        return DIP.correlate2dArray(f, DIP.rot180(w));
    };

    // ---- 2D correlation on a flat grayscale image (Uint8Array) with a small kernel ----
    DIP.correlateImage = function(gray, width, height, kernel, kw, kh) {
        var a = (kh / 2) | 0, b = (kw / 2) | 0;
        var out = new Float32Array(width * height);
        for (var y = 0; y < height; y++) {
            for (var x = 0; x < width; x++) {
                var s = 0;
                for (var i = 0; i < kh; i++) {
                    var sy = y + i - a;
                    if (sy < 0) sy = 0; else if (sy >= height) sy = height - 1; // replicate border
                    for (var j = 0; j < kw; j++) {
                        var sx = x + j - b;
                        if (sx < 0) sx = 0; else if (sx >= width) sx = width - 1;
                        s += kernel[i * kw + j] * gray[sy * width + sx];
                    }
                }
                out[y * width + x] = s;
            }
        }
        return out;
    };

    // ---- 2D convolution on a flat grayscale image (= correlate with rotated kernel) ----
    DIP.convolveImage = function(gray, width, height, kernel, kw, kh) {
        var rot = new Float32Array(kw * kh);
        for (var i = 0; i < kh; i++)
            for (var j = 0; j < kw; j++)
                rot[i * kw + j] = kernel[(kh - 1 - i) * kw + (kw - 1 - j)];
        return DIP.correlateImage(gray, width, height, rot, kw, kh);
    };

    // ---- Convert a Float32Array (any range) to a Uint8Array clamped to 0-255 ----
    DIP.clamp01_255 = function(arr) {
        var out = new Uint8Array(arr.length);
        for (var i = 0; i < arr.length; i++) {
            var v = arr[i];
            if (v < 0) out[i] = 0;
            else if (v > 255) out[i] = 255;
            else out[i] = v | 0;
        }
        return out;
    };

    // ---- Min-max normalize a Float32Array to Uint8 0-255 ----
    DIP.normalizeUint8 = function(arr) {
        var mn = Infinity, mx = -Infinity;
        for (var i = 0; i < arr.length; i++) {
            if (arr[i] < mn) mn = arr[i];
            if (arr[i] > mx) mx = arr[i];
        }
        var range = mx - mn;
        var out = new Uint8Array(arr.length);
        if (range < 1e-9) return out;
        for (var i = 0; i < arr.length; i++) {
            out[i] = Math.round((arr[i] - mn) * 255 / range);
        }
        return out;
    };

    // ============================================================
    // Practical 8: Spatial Filtering (Box, Median, Laplacian, Sobel)
    // ============================================================

    // ---- Box (mean) filter with k x k kernel ----
    DIP.boxFilter = function(gray, width, height, k) {
        var kernel = new Float32Array(k * k);
        var inv = 1.0 / (k * k);
        for (var i = 0; i < k * k; i++) kernel[i] = inv;
        var out = DIP.correlateImage(gray, width, height, kernel, k, k);
        return DIP.clamp01_255(out);
    };

    // ---- Median filter with k x k kernel ----
    DIP.medianFilter = function(gray, width, height, k) {
        var pad = (k / 2) | 0;
        var out = new Uint8Array(width * height);
        var window = new Array(k * k);
        for (var y = 0; y < height; y++) {
            for (var x = 0; x < width; x++) {
                var idx = 0;
                for (var i = -pad; i <= pad; i++) {
                    var sy = y + i;
                    if (sy < 0) sy = 0; else if (sy >= height) sy = height - 1;
                    for (var j = -pad; j <= pad; j++) {
                        var sx = x + j;
                        if (sx < 0) sx = 0; else if (sx >= width) sx = width - 1;
                        window[idx++] = gray[sy * width + sx];
                    }
                }
                window.sort(function(a, b) { return a - b; });
                out[y * width + x] = window[(k * k) >> 1];
            }
        }
        return out;
    };

    // ---- Laplacian operator (4-neighbour or 8-neighbour). Returns Float32Array. ----
    DIP.laplacian = function(gray, width, height, neighbours) {
        var k;
        if (neighbours === 8) {
            k = new Float32Array([-1,-1,-1, -1,8,-1, -1,-1,-1]);
        } else {
            k = new Float32Array([0,-1,0, -1,4,-1, 0,-1,0]);
        }
        return DIP.correlateImage(gray, width, height, k, 3, 3);
    };

    // ---- Sharpen by subtracting Laplacian response: g = f - lap(f) ----
    DIP.laplacianSharpen = function(gray, width, height, neighbours) {
        var lap = DIP.laplacian(gray, width, height, neighbours);
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) {
            var v = gray[i] - lap[i];
            if (v < 0) v = 0; else if (v > 255) v = 255;
            out[i] = v | 0;
        }
        return out;
    };

    // ---- Sobel gradient: returns {Gx, Gy, Gmag (Uint8 normalized), Gtheta (radians)} ----
    DIP.sobel = function(gray, width, height) {
        var sx = new Float32Array([-1,0,1, -2,0,2, -1,0,1]);
        var sy = new Float32Array([-1,-2,-1, 0,0,0, 1,2,1]);
        var Gx = DIP.correlateImage(gray, width, height, sx, 3, 3);
        var Gy = DIP.correlateImage(gray, width, height, sy, 3, 3);
        var mag = new Float32Array(Gx.length);
        var theta = new Float32Array(Gx.length);
        for (var i = 0; i < Gx.length; i++) {
            mag[i] = Math.abs(Gx[i]) + Math.abs(Gy[i]);
            theta[i] = Math.atan2(Gy[i], Gx[i]);
        }
        return {
            Gx: Gx, Gy: Gy,
            GxAbs: DIP.normalizeUint8(Gx.map(Math.abs)),
            GyAbs: DIP.normalizeUint8(Gy.map(Math.abs)),
            Gmag: DIP.normalizeUint8(mag),
            GthetaUint8: (function() {
                var t = new Uint8Array(theta.length);
                for (var i = 0; i < theta.length; i++) {
                    t[i] = ((theta[i] + Math.PI) / (2 * Math.PI) * 255) | 0;
                }
                return t;
            })(),
        };
    };

    // ---- Threshold a Uint8Array to a binary 0/255 image ----
    DIP.threshold = function(gray, t) {
        var out = new Uint8Array(gray.length);
        for (var i = 0; i < gray.length; i++) out[i] = gray[i] > t ? 255 : 0;
        return out;
    };

    // ---- Add salt-and-pepper noise to a grayscale image ----
    DIP.saltPepperNoise = function(gray, prob) {
        var out = new Uint8Array(gray);
        var n = gray.length;
        for (var i = 0; i < n; i++) {
            var r = Math.random();
            if (r < prob / 2) out[i] = 0;
            else if (r < prob) out[i] = 255;
        }
        return out;
    };

    // ---- Absolute difference of two Uint8 grayscale arrays ----
    DIP.absDiff = function(a, b) {
        var n = Math.min(a.length, b.length);
        var out = new Uint8Array(n);
        for (var i = 0; i < n; i++) {
            var d = a[i] - b[i];
            out[i] = d < 0 ? -d : d;
        }
        return out;
    };

    // ---- Histogram matching (specification) ----
    DIP.histMatch = function(srcGray, tgtGray) {
        var srcHist = DIP.histogram(srcGray);
        var tgtHist = DIP.histogram(tgtGray);
        var srcPdf = DIP.pdf(srcHist);
        var tgtPdf = DIP.pdf(tgtHist);
        var srcCdf = DIP.cdf(srcPdf);
        var tgtCdf = DIP.cdf(tgtPdf);
        var lut = new Uint8Array(256);
        for (var r = 0; r < 256; r++) {
            var minDiff = 2.0;
            var bestZ = 0;
            for (var z = 0; z < 256; z++) {
                var diff = Math.abs(tgtCdf[z] - srcCdf[r]);
                if (diff < minDiff) { minDiff = diff; bestZ = z; }
            }
            lut[r] = bestZ;
        }
        var out = new Uint8Array(srcGray.length);
        for (var i = 0; i < srcGray.length; i++) out[i] = lut[srcGray[i]];
        return out;
    };
})();
