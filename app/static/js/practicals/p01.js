/**
 * DIP Practical 1 - Image Fundamentals & Spatial Differencing
 * Loads the full app.js monolith which contains all P1 functionality.
 *
 * In future refactoring, P1-specific logic (spatial differencing,
 * pixel arithmetic, bit depth, surface plot, step-by-step pipeline,
 * image gallery, matplotlib reference, etc.) will be extracted from
 * app.js into this file.
 */
(function () {
    'use strict';

    // Dynamically load app.js which contains all P1 interactive features.
    // This avoids duplicating code while we transition to the multi-page structure.
    var script = document.createElement('script');
    script.src = '/static/js/app.js?v=4';
    script.async = false;
    document.body.appendChild(script);
})();
