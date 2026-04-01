/**
 * DIP Practical - Core Utilities (Static Edition)
 * Shared helper functions used across all pages.
 */
(function () {
    'use strict';

    window.DIP = window.DIP || {};

    // ---- Toast notification ----
    DIP.showToast = function(message, duration) {
        if (typeof duration === 'undefined') duration = 3000;
        var toast = document.getElementById('toast');
        if (!toast) return;
        toast.textContent = '';
        setTimeout(function () {
            toast.textContent = message;
            toast.classList.add('visible');
        }, 0);
        setTimeout(function () { toast.classList.remove('visible'); }, duration);
    };

    // ---- Loading overlay ----
    DIP.setLoading = function(container, loading) {
        if (!container) return;
        var existing = container.querySelector('.loading-overlay');
        if (loading && !existing) {
            container.setAttribute('aria-busy', 'true');
            var overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.setAttribute('role', 'status');
            var spinner = document.createElement('span');
            spinner.className = 'loading-spinner';
            spinner.textContent = 'Processing\u2026';
            overlay.appendChild(spinner);
            container.style.position = 'relative';
            container.appendChild(overlay);
        } else if (!loading && existing) {
            container.removeAttribute('aria-busy');
            existing.remove();
        }
    };

    // ---- DOM helper ----
    DIP.createEl = function(tag, className, textContent) {
        var el = document.createElement(tag);
        if (className) el.className = className;
        if (textContent !== undefined && textContent !== null) el.textContent = textContent;
        return el;
    };

    // ---- Clamp to 0-255 ----
    DIP.clamp255 = function(v) {
        return Math.max(0, Math.min(255, Math.round(v)));
    };

    // ---- Get theme-aware colors ----
    DIP.themeColors = function() {
        var s = getComputedStyle(document.documentElement);
        return {
            text: s.getPropertyValue('--text').trim(),
            muted: s.getPropertyValue('--text-muted').trim(),
            border: s.getPropertyValue('--border').trim(),
            surface1: s.getPropertyValue('--surface-1').trim(),
            surface2: s.getPropertyValue('--surface-2').trim(),
            accent: s.getPropertyValue('--accent').trim(),
        };
    };
})();
