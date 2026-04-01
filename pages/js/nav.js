/**
 * DIP Practical - Navigation (Static Edition)
 * Sets active nav link based on current page filename.
 */
(function () {
    'use strict';

    function init() {
        var path = location.pathname;
        var page = path.split('/').pop().replace('.html', '') || 'index';
        if (page === '' || path.endsWith('/')) page = 'index';

        document.querySelectorAll('[data-page]').forEach(function(link) {
            if (link.getAttribute('data-page') === page) {
                link.classList.add('active');
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
