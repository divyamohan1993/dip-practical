/**
 * DIP Practical - Interactive Enhancements
 * Scroll-based section reveal, animated counters, tab switching.
 */
(function () {
    'use strict';

    // ---- Scroll-based Section Reveal ----
    function initSectionReveal() {
        if (!('IntersectionObserver' in window)) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('section[id]').forEach(function (section) {
            observer.observe(section);
        });
    }

    // ---- Animated Number Counters ----
    function initAnimatedCounters() {
        if (!('IntersectionObserver' in window)) return;

        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var card = entry.target;
                var valueEl = card.querySelector('.stat-value');
                if (!valueEl || valueEl.dataset.animated === 'true') return;

                var text = valueEl.textContent.trim();
                if (text === '--' || text === '') return;

                var cleaned = text.replace(/,/g, '').replace(/%/g, '');
                var num = parseFloat(cleaned);
                if (isNaN(num)) return;

                valueEl.dataset.animated = 'true';
                var hasPct = text.indexOf('%') !== -1;
                var suffix = hasPct ? '%' : '';
                var isFloat = text.indexOf('.') !== -1;
                var startTime = null;
                var duration = 900;

                function step(timestamp) {
                    if (!startTime) startTime = timestamp;
                    var progress = Math.min((timestamp - startTime) / duration, 1);
                    var eased = 1 - Math.pow(1 - progress, 3);
                    var current = num * eased;
                    if (isFloat) {
                        valueEl.textContent = current.toFixed(2) + suffix;
                    } else {
                        valueEl.textContent = Math.round(current).toLocaleString() + suffix;
                    }
                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else {
                        valueEl.textContent = text;
                    }
                }
                requestAnimationFrame(step);
            });
        }, { threshold: 0.3 });

        document.querySelectorAll('.stat-card').forEach(function (card) {
            observer.observe(card);
        });
    }

    // ---- Tabs ----
    function initTabs() {
        document.querySelectorAll('.tab-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                var tabGroup = btn.closest('.panel-body') || btn.closest('section');
                if (!tabGroup) return;
                var tabId = btn.dataset.tab;

                btn.parentElement.querySelectorAll('.tab-btn').forEach(function (b) {
                    b.classList.remove('active');
                });
                btn.classList.add('active');

                tabGroup.querySelectorAll('.tab-content').forEach(function (tc) {
                    if (tc.id === 'tab-' + tabId) {
                        tc.classList.add('active');
                    } else {
                        tc.classList.remove('active');
                    }
                });
            });
        });
    }

    function init() {
        initSectionReveal();
        initAnimatedCounters();
        initTabs();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
