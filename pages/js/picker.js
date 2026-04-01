/**
 * DIP Practical - Image Picker (Static Edition)
 * Loads images from local data/ directory via manifest.json.
 * No server API needed — pure static file serving.
 */
(function() {
    'use strict';
    window.DIP = window.DIP || {};

    var _manifest = null;
    var _basePath = '';

    function detectBasePath() {
        // Detect the base path for relative URLs
        var scripts = document.getElementsByTagName('script');
        for (var i = 0; i < scripts.length; i++) {
            var src = scripts[i].getAttribute('src') || '';
            if (src.indexOf('picker.js') !== -1) {
                _basePath = src.replace(/js\/picker\.js.*/, '');
                break;
            }
        }
    }

    function loadManifest() {
        if (_manifest) return Promise.resolve(_manifest);
        detectBasePath();
        return fetch(_basePath + 'data/manifest.json')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                _manifest = data;
                return data;
            });
    }

    /**
     * Create a static image picker.
     * @param {string|HTMLElement} container - Container element or ID
     * @param {Object} opts - { id, label, defaultImage, onReady, onSelect }
     * @returns {Object} picker API { getSelection, onChange }
     */
    DIP.createPicker = function(container, opts) {
        opts = opts || {};
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return Promise.resolve(null);

        var changeListeners = [];

        return loadManifest().then(function(manifest) {
            var wrapper = DIP.createEl('div', 'image-picker');
            var labelText = opts.label || 'Image';
            var labelEl = DIP.createEl('label', 'picker-label', labelText);
            wrapper.appendChild(labelEl);

            var sel = document.createElement('select');
            sel.className = 'image-select';
            sel.setAttribute('aria-label', labelText);

            manifest.images.forEach(function(img) {
                var opt = document.createElement('option');
                opt.value = img.filename;
                opt.textContent = img.display_name + ' (' + img.width + '\u00d7' + img.height + ')';
                sel.appendChild(opt);
            });

            wrapper.appendChild(sel);
            container.appendChild(wrapper);

            // Set default selection
            if (opts.defaultImage) {
                var match = manifest.images.find(function(img) {
                    return img.filename.toLowerCase().indexOf(opts.defaultImage.toLowerCase()) !== -1;
                });
                if (match) sel.value = match.filename;
            }

            function getSelection() {
                var img = manifest.images.find(function(i) { return i.filename === sel.value; });
                return {
                    filename: sel.value,
                    url: _basePath + 'data/' + manifest.chapter + '/' + sel.value,
                    width: img ? img.width : 0,
                    height: img ? img.height : 0,
                };
            }

            function notifyChange() {
                var s = getSelection();
                changeListeners.forEach(function(fn) { fn(s); });
            }

            sel.addEventListener('change', notifyChange);

            var picker = {
                getSelection: getSelection,
                onChange: function(fn) { changeListeners.push(fn); },
            };

            if (opts.onReady) opts.onReady(manifest.images);

            return picker;
        });
    };
})();
