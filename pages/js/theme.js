/**
 * DIP Practical - Theme Toggle (Static Edition)
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'dip-theme';
    var TRANSITION_MS = 400;

    function getSystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark';
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

    function updateToggleUI(theme) {
        var btn = document.getElementById('themeToggle');
        if (!btn) return;
        var isDark = theme === 'dark';
        btn.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
        btn.setAttribute('title', isDark ? 'Switch to light mode' : 'Switch to dark mode');
        var label = btn.querySelector('.theme-toggle-label');
        if (label) label.textContent = isDark ? 'Light' : 'Dark';
    }

    function toggleTheme() {
        var current = getTheme();
        var next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.classList.add('theme-transitioning');
        applyTheme(next);
        localStorage.setItem(STORAGE_KEY, next);
        updateToggleUI(next);
        announceThemeChange(next);
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: next } }));
        setTimeout(function () { document.documentElement.classList.remove('theme-transitioning'); }, TRANSITION_MS);
    }

    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            if (!localStorage.getItem(STORAGE_KEY)) {
                var theme = e.matches ? 'dark' : 'light';
                applyTheme(theme);
                updateToggleUI(theme);
            }
        });
    }

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

    window.DIP = window.DIP || {};
    DIP.toggleTheme = toggleTheme;
    DIP.getTheme = getTheme;
})();
