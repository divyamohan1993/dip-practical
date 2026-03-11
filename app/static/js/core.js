/**
 * DIP Practical - Core Utilities
 * Shared helper functions used across all pages.
 */
(function () {
    'use strict';

    // ---- Toast notification ----
    function showToast(message, duration) {
        if (typeof duration === 'undefined') duration = 3000;
        var toast = document.getElementById('toast');
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add('visible');
        setTimeout(function () { toast.classList.remove('visible'); }, duration);
    }

    // ---- Loading overlay ----
    function setLoading(container, loading) {
        if (!container) return;
        var existing = container.querySelector('.loading-overlay');
        if (loading && !existing) {
            var overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            var spinner = document.createElement('span');
            spinner.className = 'loading-spinner';
            spinner.textContent = 'Processing...';
            overlay.appendChild(spinner);
            container.style.position = 'relative';
            container.appendChild(overlay);
        } else if (!loading && existing) {
            existing.remove();
        }
    }

    // ---- API call helper ----
    function apiCall(url, options) {
        if (typeof options === 'undefined') options = {};
        return fetch(url, options)
            .then(function (resp) {
                if (!resp.ok) {
                    return resp.json().catch(function () { return { error: 'Request failed' }; })
                        .then(function (err) { throw new Error(err.error || 'HTTP ' + resp.status); });
                }
                return resp.json();
            })
            .catch(function (e) {
                showToast('Error: ' + e.message, 5000);
                throw e;
            });
    }

    // ---- DOM helper ----
    function createEl(tag, className, textContent) {
        var el = document.createElement(tag);
        if (className) el.className = className;
        if (textContent !== undefined && textContent !== null) el.textContent = textContent;
        return el;
    }

    // ---- Clamp to 0-255 ----
    function clamp255(v) {
        return Math.max(0, Math.min(255, Math.round(v)));
    }

    // ---- Animate numeric value ----
    function animateValue(element, start, end, duration) {
        if (typeof duration === 'undefined') duration = 800;
        if (start === end) return;
        var isFloat = String(end).indexOf('.') !== -1;
        var startTime = null;
        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = start + (end - start) * eased;
            if (isFloat) {
                element.textContent = current.toFixed(2);
            } else {
                element.textContent = Math.round(current).toLocaleString();
            }
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }
        requestAnimationFrame(step);
    }

    // Expose on window for other scripts
    window.DIP = window.DIP || {};
    window.DIP.showToast = showToast;
    window.DIP.setLoading = setLoading;
    window.DIP.apiCall = apiCall;
    window.DIP.createEl = createEl;
    window.DIP.clamp255 = clamp255;
    window.DIP.animateValue = animateValue;
})();
