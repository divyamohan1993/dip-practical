/**
 * DIP Practical - Theme Toggle
 * Dark/light mode with localStorage persistence, OS preference fallback,
 * smooth transition animation, and screen reader announcements.
 *
 * IMPORTANT: The inline script in base.html sets data-theme on <html>
 * before CSS loads (FOUC prevention). This file handles the toggle UI.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'dip-theme';
    var TRANSITION_MS = 400;

    function getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    function getTheme() {
        return document.documentElement.getAttribute('data-theme') || getSystemTheme();
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
    }

    function announceThemeChange(theme) {
        var msg = document.createElement('div');
        msg.setAttribute('role', 'status');
        msg.setAttribute('aria-live', 'polite');
        msg.className = 'sr-only';
        msg.textContent = 'Color scheme changed to ' + theme + ' mode';
        document.body.appendChild(msg);
        setTimeout(function () { msg.remove(); }, 1500);
    }

    function toggleTheme() {
        var current = getTheme();
        var next = current === 'dark' ? 'light' : 'dark';

        // Smooth transition class
        document.documentElement.classList.add('theme-transitioning');

        applyTheme(next);
        localStorage.setItem(STORAGE_KEY, next);

        // Update toggle button state
        updateToggleUI(next);

        // Announce for screen readers
        announceThemeChange(next);

        // Dispatch event for JS components (e.g. canvas redraws)
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));

        // Remove transition class after animation
        setTimeout(function () {
            document.documentElement.classList.remove('theme-transitioning');
        }, TRANSITION_MS);
    }

    function updateToggleUI(theme) {
        var btn = document.getElementById('themeToggle');
        if (!btn) return;
        var isDark = theme === 'dark';
        btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
        btn.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');
    }

    // Listen for OS theme changes (only if no user override)
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            if (!localStorage.getItem(STORAGE_KEY)) {
                var theme = e.matches ? 'dark' : 'light';
                applyTheme(theme);
                updateToggleUI(theme);
            }
        });
    }

    // Initialize toggle button on DOM ready
    function init() {
        var btn = document.getElementById('themeToggle');
        if (btn) {
            btn.addEventListener('click', toggleTheme);
            updateToggleUI(getTheme());
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose on DIP namespace
    window.DIP = window.DIP || {};
    window.DIP.toggleTheme = toggleTheme;
    window.DIP.getTheme = getTheme;
})();
