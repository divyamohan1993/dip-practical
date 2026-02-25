/**
 * DIP Practical - Interactive Image Processing Application
 * Course: CSU2543 Digital Image Processing
 * Shoolini University
 */

(function () {
    'use strict';

    // State
    let availableImages = [];
    let recommendedPairs = [];
    let currentPair = null;

    // --- Utility ---
    function showToast(message, duration = 3000) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.classList.add('visible');
        setTimeout(() => toast.classList.remove('visible'), duration);
    }

    function setLoading(container, loading) {
        const existing = container.querySelector('.loading-overlay');
        if (loading && !existing) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            const spinner = document.createElement('span');
            spinner.className = 'loading-spinner';
            spinner.textContent = 'Processing...';
            overlay.appendChild(spinner);
            container.style.position = 'relative';
            container.appendChild(overlay);
        } else if (!loading && existing) {
            existing.remove();
        }
    }

    async function apiCall(url, options = {}) {
        try {
            const resp = await fetch(url, options);
            if (!resp.ok) {
                const err = await resp.json().catch(() => ({ error: 'Request failed' }));
                throw new Error(err.error || 'HTTP ' + resp.status);
            }
            return await resp.json();
        } catch (e) {
            showToast('Error: ' + e.message, 5000);
            throw e;
        }
    }

    function createEl(tag, className, textContent) {
        const el = document.createElement(tag);
        if (className) el.className = className;
        if (textContent) el.textContent = textContent;
        return el;
    }

    // --- Tabs ---
    function initTabs() {
        document.querySelectorAll('.tab-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const tabGroup = btn.closest('.panel-body') || btn.closest('section');
                const tabId = btn.dataset.tab;

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

    // --- Navigation ---
    function initNav() {
        var navLinks = document.querySelectorAll('.nav-bar a');
        navLinks.forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.forEach(function (l) { l.classList.remove('active'); });
                link.classList.add('active');
            });
        });

        var sections = document.querySelectorAll('section[id]');
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

    // --- Load Images ---
    async function loadImages() {
        var data = await apiCall('/api/images');
        availableImages = data.images;
        recommendedPairs = data.recommended_pairs;

        populateSelectors();
        populateGallery();
        populateRecommendedPairs();
    }

    function populateSelectors() {
        var sel1 = document.getElementById('select-img1');
        var sel2 = document.getElementById('select-img2');

        sel1.textContent = '';
        sel2.textContent = '';

        var defaultOpt1 = document.createElement('option');
        defaultOpt1.value = '';
        defaultOpt1.textContent = '-- Select an image --';
        sel1.appendChild(defaultOpt1);

        var defaultOpt2 = document.createElement('option');
        defaultOpt2.value = '';
        defaultOpt2.textContent = '-- Select an image --';
        sel2.appendChild(defaultOpt2);

        availableImages.forEach(function (img) {
            var opt1 = document.createElement('option');
            opt1.value = img.filename;
            opt1.textContent = img.display_name + ' (' + img.width + 'x' + img.height + ')';
            sel1.appendChild(opt1);

            var opt2 = document.createElement('option');
            opt2.value = img.filename;
            opt2.textContent = img.display_name + ' (' + img.width + 'x' + img.height + ')';
            sel2.appendChild(opt2);
        });

        document.getElementById('btn-compute-custom').disabled = false;
        document.getElementById('btn-histogram-1').disabled = false;
        document.getElementById('btn-histogram-2').disabled = false;
    }

    function populateGallery() {
        var gallery = document.getElementById('image-gallery');
        gallery.textContent = '';

        availableImages.forEach(function (img) {
            var item = createEl('div', 'gallery-item');

            var imgEl = document.createElement('img');
            imgEl.alt = img.display_name;
            imgEl.dataset.filename = img.filename;
            imgEl.loading = 'lazy';
            item.appendChild(imgEl);

            var label = createEl('div', 'gallery-label', img.display_name);
            label.title = img.display_name;
            item.appendChild(label);

            item.addEventListener('click', function () {
                loadHistogramForGallery(img.filename);
            });

            gallery.appendChild(item);
            loadGalleryImage(imgEl, img.filename);
        });
    }

    async function loadGalleryImage(imgEl, filename) {
        try {
            var data = await apiCall('/api/image/' + encodeURIComponent(filename));
            imgEl.src = 'data:image/png;base64,' + data.image;
        } catch (e) {
            imgEl.alt = 'Failed to load';
        }
    }

    async function loadHistogramForGallery(filename) {
        var container = document.getElementById('histogram-container');
        container.classList.remove('hidden');
        setLoading(container, true);

        try {
            var data = await apiCall('/api/histogram', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: filename })
            });
            document.getElementById('histogram-img').src = 'data:image/png;base64,' + data.histogram;
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            showToast('Histogram generated');
        } finally {
            setLoading(container, false);
        }
    }

    function populateRecommendedPairs() {
        var container = document.getElementById('pair-cards-container');
        container.textContent = '';

        recommendedPairs.forEach(function (pair) {
            var card = createEl('div', 'pair-card');

            var badge = createEl('span', 'pair-badge', pair.id.replace(/_/g, ' '));
            card.appendChild(badge);

            var heading = createEl('h4', null, pair.name);
            card.appendChild(heading);

            var desc = createEl('p', null, pair.description);
            card.appendChild(desc);

            card.addEventListener('click', function () {
                computeRecommendedPair(pair);
            });

            container.appendChild(card);
        });
    }

    // --- Compute Spatial Difference ---
    async function computeRecommendedPair(pair) {
        currentPair = pair;
        await computeDifference(pair.image1, pair.image2, pair);
    }

    async function computeCustomPair() {
        var img1 = document.getElementById('select-img1').value;
        var img2 = document.getElementById('select-img2').value;
        if (!img1 || !img2) {
            showToast('Please select both images');
            return;
        }
        if (img1 === img2) {
            showToast('Select two different images');
            return;
        }
        currentPair = null;
        await computeDifference(img1, img2, null);
    }

    async function computeDifference(filename1, filename2, pair) {
        var resultContainer = document.getElementById('result-container');
        resultContainer.classList.remove('hidden');
        setLoading(resultContainer, true);

        try {
            var data = await apiCall('/api/spatial-difference', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: filename1, image2: filename2 })
            });

            // Display images
            document.getElementById('result-img1').src = 'data:image/png;base64,' + data.image1;
            document.getElementById('result-img2').src = 'data:image/png;base64,' + data.image2;
            document.getElementById('result-diff').src = 'data:image/png;base64,' + data.difference;
            document.getElementById('result-diff-enhanced').src = 'data:image/png;base64,' + data.difference_enhanced;

            // Captions
            document.getElementById('caption-img1').textContent = 'Image 1: ' + getDisplayName(filename1);
            document.getElementById('caption-img2').textContent = 'Image 2: ' + getDisplayName(filename2);

            // Statistics
            var s = data.stats;
            document.getElementById('stat-mean').textContent = s.mean_difference.toFixed(2);
            document.getElementById('stat-max').textContent = String(s.max_difference);
            document.getElementById('stat-std').textContent = s.std_difference.toFixed(2);
            document.getElementById('stat-nonzero').textContent = s.nonzero_pixels.toLocaleString();
            document.getElementById('stat-pct').textContent = s.nonzero_percentage + '%';
            document.getElementById('stat-size').textContent = s.final_shape[1] + 'x' + s.final_shape[0];

            // Theory block for recommended pairs
            var theoryBlock = document.getElementById('result-theory');
            if (pair) {
                document.getElementById('result-theory-title').textContent = pair.name;
                document.getElementById('result-theory-text').textContent = pair.theory;
                theoryBlock.classList.remove('hidden');
            } else {
                theoryBlock.classList.add('hidden');
            }

            // Store for full plot
            resultContainer.dataset.img1 = filename1;
            resultContainer.dataset.img2 = filename2;

            // Reset full plot
            document.getElementById('full-plot-container').classList.add('hidden');

            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            showToast('Spatial difference computed');

        } finally {
            setLoading(resultContainer, false);
        }
    }

    function getDisplayName(filename) {
        var img = availableImages.find(function (i) { return i.filename === filename; });
        return img ? img.display_name : filename;
    }

    // --- Full Comparison Plot ---
    async function generateFullPlot() {
        var container = document.getElementById('result-container');
        var img1 = container.dataset.img1;
        var img2 = container.dataset.img2;
        if (!img1 || !img2) return;

        var plotContainer = document.getElementById('full-plot-container');
        plotContainer.classList.remove('hidden');
        setLoading(plotContainer, true);

        try {
            var data = await apiCall('/api/comparison-plot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: img1, image2: img2 })
            });
            document.getElementById('full-plot-img').src = 'data:image/png;base64,' + data.plot;
            showToast('Matplotlib comparison plot generated');
        } finally {
            setLoading(plotContainer, false);
        }
    }

    // --- Histograms ---
    async function generateHistogram(selectId) {
        var filename = document.getElementById(selectId).value;
        if (!filename) {
            showToast('Select an image first');
            return;
        }
        await loadHistogramForGallery(filename);
    }

    // --- Matplotlib Reference ---
    async function loadMatplotlibReference() {
        var data = await apiCall('/api/matplotlib-reference');
        var container = document.getElementById('matplotlib-reference-content');
        container.textContent = '';

        data.categories.forEach(function (cat) {
            var catDiv = createEl('div', 'ref-category');

            var catTitle = createEl('h3', null, cat.name);
            catDiv.appendChild(catTitle);

            cat.commands.forEach(function (cmd) {
                var cmdDiv = createEl('div', 'ref-command');

                var sig = createEl('div', 'cmd-signature', cmd.command);
                cmdDiv.appendChild(sig);

                var desc = createEl('div', 'cmd-desc', cmd.description);
                cmdDiv.appendChild(desc);

                var example = createEl('div', 'cmd-example', cmd.example);
                cmdDiv.appendChild(example);

                var tip = createEl('div', 'cmd-tip', cmd.tip);
                cmdDiv.appendChild(tip);

                catDiv.appendChild(cmdDiv);
            });

            container.appendChild(catDiv);
        });
    }

    async function loadMatplotlibDemos() {
        var container = document.getElementById('matplotlib-demos-content');
        container.textContent = '';
        var loadingMsg = createEl('div', 'loading-spinner', 'Generating plots on server...');
        container.appendChild(loadingMsg);

        var demoNames = {
            'subplot_layouts': 'Subplot Grid Layouts - plt.subplot() with various plot types',
            'colormaps': 'Colormap Variations - plt.imshow() with different colormaps on the same image',
            'figure_customization': 'Figure Customization - Annotations, polar plots, and styling'
        };

        try {
            var data = await apiCall('/api/matplotlib-demos');
            container.textContent = '';

            Object.keys(data.demos).forEach(function (key) {
                var div = createEl('div', 'demo-plot');

                var img = document.createElement('img');
                img.src = 'data:image/png;base64,' + data.demos[key];
                img.alt = demoNames[key] || key;
                div.appendChild(img);

                var caption = createEl('div', 'demo-caption', demoNames[key] || key);
                div.appendChild(caption);

                container.appendChild(div);
            });

            showToast('Matplotlib demos generated');
        } catch (e) {
            container.textContent = '';
            var errMsg = createEl('p', null, 'Failed to load demos.');
            errMsg.style.color = 'var(--red-accent)';
            container.appendChild(errMsg);
        }
    }

    // --- Event Listeners ---
    function bindEvents() {
        document.getElementById('btn-compute-custom').addEventListener('click', computeCustomPair);
        document.getElementById('btn-histogram-1').addEventListener('click', function () {
            generateHistogram('select-img1');
        });
        document.getElementById('btn-histogram-2').addEventListener('click', function () {
            generateHistogram('select-img2');
        });
        document.getElementById('btn-full-plot').addEventListener('click', generateFullPlot);
        document.getElementById('btn-load-demos').addEventListener('click', loadMatplotlibDemos);
    }

    // --- Init ---
    async function init() {
        initTabs();
        initNav();
        bindEvents();

        await Promise.all([
            loadImages(),
            loadMatplotlibReference()
        ]);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
