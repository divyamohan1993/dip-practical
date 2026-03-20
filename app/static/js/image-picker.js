/**
 * Image Picker Component for DIP Practical.
 * Two-dropdown system: Chapter (dataset) -> Image.
 * Downloads chapter datasets on-demand from public source.
 */
(function() {
    const API = '/api';
    let _chapters = null;
    const _imageCache = {};

    async function fetchChapters() {
        if (_chapters) return _chapters;
        const resp = await DIP.apiCall(`${API}/chapters`);
        _chapters = resp.chapters;
        return _chapters;
    }

    async function fetchImages(chapterId) {
        if (_imageCache[chapterId]) return _imageCache[chapterId];
        const resp = await DIP.apiCall(`${API}/chapters/${chapterId}/images`);
        _imageCache[chapterId] = resp.images;
        return resp.images;
    }

    /**
     * Create an image picker inside a container.
     * @param {HTMLElement|string} container - Container element or ID
     * @param {Object} opts
     * @param {string} opts.id - Unique picker ID
     * @param {string} opts.label - Optional label (e.g. "Image 1:")
     * @param {string} opts.defaultChapter - Default chapter (e.g. 'CH02')
     * @param {string} opts.defaultImage - Substring to match default image filename
     * @param {Function} opts.onReady - Called when images are loaded
     * @returns {Object} Picker API
     */
    DIP.createPicker = async function(container, opts) {
        opts = opts || {};
        if (typeof container === 'string') container = document.getElementById(container);
        if (!container) return null;

        var id = opts.id || 'pk_' + Math.random().toString(36).slice(2, 8);
        var defaultImage = opts.defaultImage || null;
        var changeListeners = [];

        var wrapper = document.createElement('div');
        wrapper.className = 'image-picker';

        if (opts.label) {
            var lbl = document.createElement('span');
            lbl.className = 'picker-label';
            lbl.textContent = opts.label;
            wrapper.appendChild(lbl);
        }

        var chSel = document.createElement('select');
        chSel.className = 'chapter-select';
        chSel.id = id + '_ch';

        var imgSel = document.createElement('select');
        imgSel.className = 'image-select';
        imgSel.id = id + '_img';

        wrapper.appendChild(chSel);
        wrapper.appendChild(imgSel);
        container.appendChild(wrapper);

        // Populate chapters
        var chapters = await fetchChapters();
        chSel.innerHTML = chapters.map(function(ch) {
            var dl = ch.downloaded ? '' : ' \u2913';
            return '<option value="' + ch.id + '">Ch ' + ch.num + ': ' + ch.name + dl + '</option>';
        }).join('');

        if (opts.defaultChapter) chSel.value = opts.defaultChapter;

        function notifyChange() {
            var sel = { chapter: chSel.value, filename: imgSel.value };
            changeListeners.forEach(function(fn) { fn(sel); });
        }

        async function loadImages() {
            var ch = chSel.value;
            imgSel.innerHTML = '<option value="">Downloading chapter...</option>';
            imgSel.disabled = true;

            try {
                var images = await fetchImages(ch);
                if (images.length === 0) {
                    imgSel.innerHTML = '<option value="">No images found</option>';
                    return;
                }
                imgSel.innerHTML = images.map(function(img) {
                    return '<option value="' + img.filename + '">' + img.display_name + ' (' + img.width + '\u00d7' + img.height + ')</option>';
                }).join('');

                if (defaultImage) {
                    var match = images.find(function(i) { return i.filename.includes(defaultImage); });
                    if (match) imgSel.value = match.filename;
                    defaultImage = null;
                }

                imgSel.disabled = false;

                // Remove download indicator
                var chOpt = chSel.querySelector('option[value="' + ch + '"]');
                if (chOpt) chOpt.textContent = chOpt.textContent.replace(' \u2913', '');

                if (opts.onReady) opts.onReady(images);
                notifyChange();
            } catch (e) {
                imgSel.innerHTML = '<option value="">Failed to load</option>';
                DIP.showToast('Failed to load chapter images');
            }
        }

        chSel.addEventListener('change', loadImages);
        imgSel.addEventListener('change', notifyChange);

        var picker = {
            getSelection: function() {
                return { chapter: chSel.value, filename: imgSel.value };
            },
            setSelection: async function(chapter, filename) {
                if (chapter && chSel.value !== chapter) {
                    chSel.value = chapter;
                    defaultImage = filename;
                    await loadImages();
                } else if (filename) {
                    imgSel.value = filename;
                    notifyChange();
                }
            },
            onChange: function(fn) {
                changeListeners.push(fn);
            },
            enable: function() {
                chSel.disabled = false;
                imgSel.disabled = false;
            },
            disable: function() {
                chSel.disabled = true;
                imgSel.disabled = true;
            }
        };

        await loadImages();
        return picker;
    };
})();
