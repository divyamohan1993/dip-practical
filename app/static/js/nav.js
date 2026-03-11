/**
 * DIP Practical - Navigation Enhancements
 * Handles scroll-spy for section-based nav and active state management.
 */
(function () {
    'use strict';

    // Scroll-spy: highlight nav section links based on scroll position
    function initScrollSpy() {
        var sections = document.querySelectorAll('section[id]');
        if (sections.length === 0) return;

        // Build a mapping of section IDs to their anchors within the page
        var navLinks = document.querySelectorAll('.nav-bar a, .dip-navbar .nav-link[href^="#"]');
        if (navLinks.length === 0) return;

        window.addEventListener('scroll', function () {
            var current = '';
            sections.forEach(function (section) {
                if (window.scrollY >= section.offsetTop - 120) {
                    current = section.getAttribute('id');
                }
            });
            navLinks.forEach(function (link) {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initScrollSpy);
    } else {
        initScrollSpy();
    }
})();
