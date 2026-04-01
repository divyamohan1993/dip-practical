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
