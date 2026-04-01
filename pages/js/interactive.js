/**
 * DIP Practical - Interactive Enhancements (Static Edition)
 * Scroll-based section reveal and animated counters.
 */
(function () {
    'use strict';

    function initSectionReveal() {
        if (!('IntersectionObserver' in window)) return;
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) entry.target.classList.add('visible');
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
        document.querySelectorAll('section[id]').forEach(function (section) {
            observer.observe(section);
        });
    }

    function init() {
        initSectionReveal();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
