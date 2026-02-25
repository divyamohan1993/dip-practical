/**
 * DIP Practical - Interactive Image Processing Application
 * Course: CSU2543 Digital Image Processing
 * Shoolini University
 *
 * Features:
 *  - Spatial Image Differencing (original)
 *  - Image gallery and histograms (original)
 *  - Matplotlib reference and demos (original)
 *  - Interactive Pixel Grid Visualization (canvas-based, 10x10)
 *  - Grayscale Bar with hover value
 *  - Pixel Arithmetic Calculator with API integration
 *  - Step-by-Step Pipeline with timeline animation
 *  - Bit Depth Comparison with image select dropdown
 *  - 3D Surface Plot
 *  - Quiz System (hardcoded data, score tracking)
 *  - Pixel Inspector on Click
 *  - Animated Number Counters (IntersectionObserver)
 *  - Scroll-based Section Reveal
 *  - Toast notifications
 */

(function () {
    'use strict';

    // ========================================================================
    // State
    // ========================================================================
    var availableImages = [];
    var recommendedPairs = [];
    var currentPair = null;
    var pixelGridData = null;
    var pixelGridCenter = { x: 0, y: 0 };
    var pixelGridFilename = null;
    var lastDiffFilename = null;

    // ========================================================================
    // Quiz Data (hardcoded)
    // ========================================================================
    var QUIZ_DATA = {
        foundations: [
            {
                question: 'How many bytes are needed to store a 512x512 image with 8 bits per pixel?',
                options: [
                    '262,144 bytes (256 KB)',
                    '2,097,152 bytes (2 MB)',
                    '524,288 bytes (512 KB)',
                    '131,072 bytes (128 KB)'
                ],
                correct: 0,
                explanation: '512 x 512 = 262,144 pixels. At 8 bits (1 byte) per pixel: 262,144 x 1 = 262,144 bytes = 256 KB.'
            },
            {
                question: 'What happens when you add 200 + 100 in uint8 (unsigned 8-bit integer)?',
                options: [
                    '300',
                    '44 (wraps around: 300 - 256 = 44)',
                    '255 (saturated)',
                    'Error'
                ],
                correct: 1,
                explanation: 'In uint8, the maximum value is 255. 200 + 100 = 300, which overflows. In NumPy/OpenCV, raw addition wraps: 300 mod 256 = 44. Use cv2.add() for saturated addition (caps at 255).'
            },
            {
                question: 'A pixel at position (x,y) has how many 4-neighbors (N4)?',
                options: ['2', '4', '8', '6'],
                correct: 1,
                explanation: 'The 4-neighbors of pixel (x,y) are: (x-1,y), (x+1,y), (x,y-1), (x,y+1) -- the pixels directly above, below, left, and right.'
            },
            {
                question: 'In the image formation model f(x,y) = i(x,y) x r(x,y), what does r(x,y) represent?',
                options: [
                    'Illumination component',
                    'Reflectance component',
                    'Resolution',
                    'Radiation'
                ],
                correct: 1,
                explanation: 'r(x,y) is the reflectance component (0 < r < 1), representing the fraction of light reflected by the object. i(x,y) is the illumination component.'
            }
        ],
        practical1: [
            {
                question: 'Why is cv2.absdiff() preferred over simple subtraction (img1 - img2) for image differencing?',
                options: [
                    "It's faster",
                    'It handles uint8 underflow correctly (no wraparound)',
                    'It produces color output',
                    'It automatically resizes images'
                ],
                correct: 1,
                explanation: 'Simple subtraction with uint8 causes underflow: 50 - 100 = 206 (wraps around) instead of the intended -50. cv2.absdiff() computes |a - b| correctly, always returning non-negative results without wraparound.'
            },
            {
                question: 'In Digital Subtraction Angiography (DSA), what does subtracting the mask from the live image reveal?',
                options: [
                    'Bone structure',
                    'Soft tissue details',
                    'Blood vessels (contrast-filled)',
                    'Skin texture'
                ],
                correct: 2,
                explanation: "DSA subtracts a pre-contrast 'mask' image from a post-contrast 'live' image. Since bones and soft tissue appear in both images, they cancel out. Only the contrast agent (in blood vessels) differs between the two, so vessels are isolated."
            },
            {
                question: 'If the mean difference between two images is 2.5 and the standard deviation is 15.3, what does this tell you?',
                options: [
                    'The images are nearly identical everywhere',
                    'Most pixels are similar but there are localized regions of large difference',
                    'The images are completely different',
                    'The computation failed'
                ],
                correct: 1,
                explanation: 'A low mean (2.5) indicates most pixels have small differences. A high standard deviation (15.3) relative to the mean indicates the differences are not uniform -- there are localized areas with much larger changes. This pattern is typical of DSA where vessels create bright spots against a mostly-zero background.'
            }
        ]
    };

    // ========================================================================
    // Utility helpers
    // ========================================================================

    function showToast(message, duration) {
        if (typeof duration === 'undefined') duration = 3000;
        var toast = document.getElementById('toast');
        if (!toast) return;
        toast.textContent = message;
        toast.classList.add('visible');
        setTimeout(function () { toast.classList.remove('visible'); }, duration);
    }

    function setLoading(container, loading) {
        if (!container) return;
        var existing = container.querySelector('.loading-overlay');
        if (loading && !existing) {
            var overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            var spinner = document.createElement('span');
            spinner.className = 'loading-spinner';
            spinner.textContent = 'Processing...';
            overlay.appendChild(spinner);
            container.style.position = 'relative';
            container.appendChild(overlay);
        } else if (!loading && existing) {
            existing.remove();
        }
    }

    async function apiCall(url, options) {
        if (typeof options === 'undefined') options = {};
        try {
            var resp = await fetch(url, options);
            if (!resp.ok) {
                var err = await resp.json().catch(function () { return { error: 'Request failed' }; });
                throw new Error(err.error || 'HTTP ' + resp.status);
            }
            return await resp.json();
        } catch (e) {
            showToast('Error: ' + e.message, 5000);
            throw e;
        }
    }

    function createEl(tag, className, textContent) {
        var el = document.createElement(tag);
        if (className) el.className = className;
        if (textContent !== undefined && textContent !== null) el.textContent = textContent;
        return el;
    }

    /**
     * Build an HTML table from a 2D array of pixel values.
     * Each cell is colored by its intensity (0 = black, 255 = white)
     * and displays the numeric value.
     */
    function createPixelTable(grid, title) {
        var wrapper = createEl('div', 'pixel-table-wrapper');
        if (title) {
            var heading = createEl('h4', 'pixel-table-title', title);
            wrapper.appendChild(heading);
        }

        var table = createEl('table', 'pixel-value-table');
        for (var r = 0; r < grid.length; r++) {
            var tr = document.createElement('tr');
            for (var c = 0; c < grid[r].length; c++) {
                var val = Math.round(grid[r][c]);
                val = Math.max(0, Math.min(255, val));
                var td = document.createElement('td');
                td.textContent = String(val);
                var bg = 'rgb(' + val + ',' + val + ',' + val + ')';
                td.style.backgroundColor = bg;
                td.style.color = val > 128 ? '#000' : '#fff';
                td.style.fontSize = '0.65rem';
                td.style.textAlign = 'center';
                td.style.padding = '2px 3px';
                td.style.minWidth = '28px';
                td.style.fontFamily = 'var(--font-mono)';
                td.title = '(' + r + ',' + c + ') = ' + val;
                tr.appendChild(td);
            }
            table.appendChild(tr);
        }
        wrapper.appendChild(table);
        return wrapper;
    }

    /**
     * Clamp a number to [0, 255].
     */
    function clamp255(v) {
        return Math.max(0, Math.min(255, Math.round(v)));
    }

    /**
     * Generate a default 10x10 gradient pattern.
     */
    function generateDefaultGrid() {
        var grid = [];
        for (var r = 0; r < 10; r++) {
            var row = [];
            for (var c = 0; c < 10; c++) {
                row.push(Math.round((r * 10 + c) * 2.55));
            }
            grid.push(row);
        }
        return grid;
    }

    // ========================================================================
    // Animated Number Counter
    // ========================================================================

    /**
     * Animate a numeric value in an element from start to end over duration ms.
     */
    function animateValue(element, start, end, duration) {
        if (typeof duration === 'undefined') duration = 800;
        if (start === end) return;
        var isFloat = String(end).indexOf('.') !== -1;
        var startTime = null;

        function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var current = start + (end - start) * eased;
            if (isFloat) {
                element.textContent = current.toFixed(2);
            } else {
                element.textContent = Math.round(current).toLocaleString();
            }
            if (progress < 1) {
                requestAnimationFrame(step);
            }
        }
        requestAnimationFrame(step);
    }

    // ========================================================================
    // Animated Number Counters via IntersectionObserver
    // ========================================================================

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

                // Attempt to parse as number
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

    // ========================================================================
    // Scroll-based Section Reveal
    // ========================================================================

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

    // ========================================================================
    // Tabs
    // ========================================================================
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

    // ========================================================================
    // Navigation
    // ========================================================================
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

    // ========================================================================
    // Load Images
    // ========================================================================
    async function loadImages() {
        var data = await apiCall('/api/images');
        availableImages = data.images;
        recommendedPairs = data.recommended_pairs;

        populateSelectors();
        populateGallery();
        populateRecommendedPairs();
        populateBitDepthSelector();
    }

    function populateSelectors() {
        var sel1 = document.getElementById('select-img1');
        var sel2 = document.getElementById('select-img2');
        if (!sel1 || !sel2) return;

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

        var btnCompute = document.getElementById('btn-compute-custom');
        var btnHist1 = document.getElementById('btn-histogram-1');
        var btnHist2 = document.getElementById('btn-histogram-2');
        if (btnCompute) btnCompute.disabled = false;
        if (btnHist1) btnHist1.disabled = false;
        if (btnHist2) btnHist2.disabled = false;
    }

    function populateGallery() {
        var gallery = document.getElementById('image-gallery');
        if (!gallery) return;
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
        if (!container) return;
        container.classList.remove('hidden');
        setLoading(container, true);

        try {
            var data = await apiCall('/api/histogram', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: filename })
            });
            var histImg = document.getElementById('histogram-img');
            if (histImg) {
                histImg.src = 'data:image/png;base64,' + data.histogram;
            }
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            showToast('Histogram generated');
        } finally {
            setLoading(container, false);
        }
    }

    function populateRecommendedPairs() {
        var container = document.getElementById('pair-cards-container');
        if (!container) return;
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

    // ========================================================================
    // Compute Spatial Difference
    // ========================================================================
    async function computeRecommendedPair(pair) {
        currentPair = pair;
        await computeDifference(pair.image1, pair.image2, pair);
    }

    async function computeCustomPair() {
        var sel1 = document.getElementById('select-img1');
        var sel2 = document.getElementById('select-img2');
        if (!sel1 || !sel2) return;
        var img1 = sel1.value;
        var img2 = sel2.value;
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
        if (!resultContainer) return;
        resultContainer.classList.remove('hidden');
        setLoading(resultContainer, true);

        try {
            var data = await apiCall('/api/spatial-difference', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: filename1, image2: filename2 })
            });

            // Display images
            var rImg1 = document.getElementById('result-img1');
            var rImg2 = document.getElementById('result-img2');
            var rDiff = document.getElementById('result-diff');
            var rDiffE = document.getElementById('result-diff-enhanced');
            if (rImg1) rImg1.src = 'data:image/png;base64,' + data.image1;
            if (rImg2) rImg2.src = 'data:image/png;base64,' + data.image2;
            if (rDiff) rDiff.src = 'data:image/png;base64,' + data.difference;
            if (rDiffE) rDiffE.src = 'data:image/png;base64,' + data.difference_enhanced;

            // Store difference filename
            if (data.difference_filename) {
                lastDiffFilename = data.difference_filename;
            }

            // Captions
            var cap1 = document.getElementById('caption-img1');
            var cap2 = document.getElementById('caption-img2');
            if (cap1) cap1.textContent = 'Image 1: ' + getDisplayName(filename1);
            if (cap2) cap2.textContent = 'Image 2: ' + getDisplayName(filename2);

            // Statistics with animated counters
            var s = data.stats;
            animateStatValue('stat-mean', s.mean_difference, true);
            animateStatValue('stat-max', s.max_difference, false);
            animateStatValue('stat-std', s.std_difference, true);
            animateStatValue('stat-nonzero', s.nonzero_pixels, false);
            var statPct = document.getElementById('stat-pct');
            if (statPct) statPct.textContent = s.nonzero_percentage + '%';
            var statSize = document.getElementById('stat-size');
            if (statSize) statSize.textContent = s.final_shape[1] + 'x' + s.final_shape[0];

            // Theory block for recommended pairs
            var theoryBlock = document.getElementById('result-theory');
            if (theoryBlock) {
                if (pair) {
                    var theoryTitle = document.getElementById('result-theory-title');
                    var theoryText = document.getElementById('result-theory-text');
                    if (theoryTitle) theoryTitle.textContent = pair.name;
                    if (theoryText) theoryText.textContent = pair.theory;
                    theoryBlock.classList.remove('hidden');
                } else {
                    theoryBlock.classList.add('hidden');
                }
            }

            // Store for full plot
            resultContainer.dataset.img1 = filename1;
            resultContainer.dataset.img2 = filename2;

            // Reset full plot
            var fpContainer = document.getElementById('full-plot-container');
            if (fpContainer) fpContainer.classList.add('hidden');

            resultContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            showToast('Spatial difference computed');

        } finally {
            setLoading(resultContainer, false);
        }
    }

    /**
     * Helper: animate a stat-card value.
     */
    function animateStatValue(elementId, targetValue, isFloat) {
        var el = document.getElementById(elementId);
        if (!el) return;
        animateValue(el, 0, targetValue, 900);
    }

    function getDisplayName(filename) {
        var img = availableImages.find(function (i) { return i.filename === filename; });
        return img ? img.display_name : filename;
    }

    // ========================================================================
    // Full Comparison Plot
    // ========================================================================
    async function generateFullPlot() {
        var container = document.getElementById('result-container');
        if (!container) return;
        var img1 = container.dataset.img1;
        var img2 = container.dataset.img2;
        if (!img1 || !img2) return;

        var plotContainer = document.getElementById('full-plot-container');
        if (!plotContainer) return;
        plotContainer.classList.remove('hidden');
        setLoading(plotContainer, true);

        try {
            var data = await apiCall('/api/comparison-plot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: img1, image2: img2 })
            });
            var plotImg = document.getElementById('full-plot-img');
            if (plotImg) plotImg.src = 'data:image/png;base64,' + data.plot;
            showToast('Matplotlib comparison plot generated');
        } finally {
            setLoading(plotContainer, false);
        }
    }

    // ========================================================================
    // Histograms
    // ========================================================================
    async function generateHistogram(selectId) {
        var sel = document.getElementById(selectId);
        if (!sel) return;
        var filename = sel.value;
        if (!filename) {
            showToast('Select an image first');
            return;
        }
        await loadHistogramForGallery(filename);
    }

    // ========================================================================
    // Matplotlib Reference
    // ========================================================================
    async function loadMatplotlibReference() {
        var data = await apiCall('/api/matplotlib-reference');
        var container = document.getElementById('matplotlib-reference-content');
        if (!container) return;
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
        if (!container) return;
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

    // ========================================================================
    // 1. Pixel Grid Visualization (Canvas-based, 10x10)
    // ========================================================================

    function initPixelGrid() {
        var container = document.getElementById('pixel-grid-canvas-container');
        if (!container) {
            // Fallback: try legacy container name
            container = document.getElementById('pixel-grid-container');
        }
        if (!container) return;

        // Generate default grid
        pixelGridData = generateDefaultGrid();
        renderPixelGridCanvas(container, pixelGridData);
    }

    function attemptLoadPixelGridFromImage() {
        if (availableImages.length === 0) return;
        pixelGridFilename = availableImages[0].filename;
        pixelGridCenter = { x: 0, y: 0 };

        apiCall('/api/pixel-view', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: pixelGridFilename, x: 0, y: 0, size: 10 })
        }).then(function (data) {
            if (data && data.pixel_grid) {
                pixelGridData = data.pixel_grid.slice(0, 10).map(function (row) {
                    return row.slice(0, 10);
                });
                var container = document.getElementById('pixel-grid-canvas-container')
                    || document.getElementById('pixel-grid-container');
                if (container) {
                    renderPixelGridCanvas(container, pixelGridData);
                }
            }
        }).catch(function () {
            // Silently keep default gradient grid
        });
    }

    function renderPixelGridCanvas(container, grid) {
        container.textContent = '';

        var label = createEl('div', 'pixel-grid-label', 'Interactive Pixel Grid (10x10) -- Hover for details, click to re-center');
        container.appendChild(label);

        var CELL_SIZE = 40;
        var rows = grid.length;
        var cols = grid[0] ? grid[0].length : 0;
        var canvasWidth = cols * CELL_SIZE;
        var canvasHeight = rows * CELL_SIZE;

        var canvas = document.createElement('canvas');
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;
        canvas.style.maxWidth = '100%';
        canvas.style.cursor = 'crosshair';
        canvas.style.border = '1px solid var(--leather-light, #8d6e63)';
        canvas.style.borderRadius = '6px';
        canvas.className = 'pixel-grid-canvas';

        var ctx = canvas.getContext('2d');

        // Draw cells
        function drawGrid() {
            for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                    var val = clamp255(grid[r][c]);
                    ctx.fillStyle = 'rgb(' + val + ',' + val + ',' + val + ')';
                    ctx.fillRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);

                    // Grid line
                    ctx.strokeStyle = 'rgba(128, 128, 128, 0.3)';
                    ctx.lineWidth = 0.5;
                    ctx.strokeRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);

                    // Value text
                    ctx.fillStyle = val > 128 ? '#1a1a1a' : '#f0f0f0';
                    ctx.font = '11px monospace';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(String(val), c * CELL_SIZE + CELL_SIZE / 2, r * CELL_SIZE + CELL_SIZE / 2);
                }
            }
        }
        drawGrid();

        // Tooltip element
        var tooltip = createEl('div', 'pixel-grid-tooltip');
        tooltip.style.display = 'none';
        tooltip.style.position = 'absolute';
        tooltip.style.pointerEvents = 'none';
        tooltip.style.background = 'rgba(0,0,0,0.85)';
        tooltip.style.color = '#fff';
        tooltip.style.padding = '6px 10px';
        tooltip.style.borderRadius = '4px';
        tooltip.style.fontSize = '0.8rem';
        tooltip.style.fontFamily = 'var(--font-mono, monospace)';
        tooltip.style.zIndex = '100';
        tooltip.style.whiteSpace = 'nowrap';

        var canvasWrapper = createEl('div', 'pixel-grid-canvas-wrapper');
        canvasWrapper.style.position = 'relative';
        canvasWrapper.style.display = 'inline-block';
        canvasWrapper.appendChild(canvas);
        canvasWrapper.appendChild(tooltip);
        container.appendChild(canvasWrapper);

        // Hover: highlight cell and show tooltip
        var lastHighlight = { r: -1, c: -1 };
        canvas.addEventListener('mousemove', function (e) {
            var rect = canvas.getBoundingClientRect();
            var scaleX = canvas.width / rect.width;
            var scaleY = canvas.height / rect.height;
            var mx = (e.clientX - rect.left) * scaleX;
            var my = (e.clientY - rect.top) * scaleY;
            var col = Math.floor(mx / CELL_SIZE);
            var row = Math.floor(my / CELL_SIZE);

            if (row < 0 || row >= rows || col < 0 || col >= cols) {
                tooltip.style.display = 'none';
                if (lastHighlight.r >= 0) {
                    drawGrid();
                    lastHighlight = { r: -1, c: -1 };
                }
                return;
            }

            var val = clamp255(grid[row][col]);
            var actualRow = pixelGridCenter.y + row;
            var actualCol = pixelGridCenter.x + col;
            tooltip.textContent = '(' + actualCol + ', ' + actualRow + ') = ' + val + '  |  binary: ' + ('00000000' + val.toString(2)).slice(-8);
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX - canvasWrapper.getBoundingClientRect().left + 12) + 'px';
            tooltip.style.top = (e.clientY - canvasWrapper.getBoundingClientRect().top - 30) + 'px';

            // Redraw grid then highlight cell
            if (lastHighlight.r !== row || lastHighlight.c !== col) {
                drawGrid();
                ctx.strokeStyle = '#FFD700';
                ctx.lineWidth = 2.5;
                ctx.strokeRect(col * CELL_SIZE + 1, row * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2);
                lastHighlight = { r: row, c: col };
            }
        });

        canvas.addEventListener('mouseleave', function () {
            tooltip.style.display = 'none';
            if (lastHighlight.r >= 0) {
                drawGrid();
                lastHighlight = { r: -1, c: -1 };
            }
        });

        // Click: re-center on this pixel position
        canvas.addEventListener('click', function (e) {
            if (!pixelGridFilename) return;
            var rect = canvas.getBoundingClientRect();
            var scaleX = canvas.width / rect.width;
            var scaleY = canvas.height / rect.height;
            var mx = (e.clientX - rect.left) * scaleX;
            var my = (e.clientY - rect.top) * scaleY;
            var col = Math.floor(mx / CELL_SIZE);
            var row = Math.floor(my / CELL_SIZE);

            if (row < 0 || row >= rows || col < 0 || col >= cols) return;

            var newX = pixelGridCenter.x + col;
            var newY = pixelGridCenter.y + row;

            showToast('Loading pixel region at (' + newX + ', ' + newY + ')...');

            apiCall('/api/pixel-view', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: pixelGridFilename, x: newX, y: newY, size: 10 })
            }).then(function (data) {
                if (data && data.pixel_grid) {
                    pixelGridCenter = { x: newX, y: newY };
                    pixelGridData = data.pixel_grid.slice(0, 10).map(function (row) {
                        return row.slice(0, 10);
                    });
                    renderPixelGridCanvas(container, pixelGridData);
                    showToast('Pixel grid re-centered at (' + newX + ', ' + newY + ')');
                }
            }).catch(function () {
                showToast('Failed to load pixel data at that position');
            });
        });

        // Info about current position
        var infoDiv = createEl('div', 'pixel-grid-info');
        infoDiv.style.marginTop = '8px';
        infoDiv.style.fontSize = '0.8rem';
        infoDiv.style.color = 'var(--ink-light, #666)';
        infoDiv.textContent = 'Showing region from (' + pixelGridCenter.x + ', ' + pixelGridCenter.y + ') -- Image: ' + (pixelGridFilename || 'default gradient');
        container.appendChild(infoDiv);
    }

    // ========================================================================
    // 2. Grayscale Bar
    // ========================================================================

    function initGrayscaleBar() {
        var container = document.getElementById('grayscale-bar');
        if (!container) return;

        container.textContent = '';

        var barLabel = createEl('div', 'grayscale-bar-label', '0-255 Grayscale Intensity Gradient');
        barLabel.style.marginBottom = '8px';
        barLabel.style.fontSize = '0.85rem';
        barLabel.style.fontWeight = '600';
        container.appendChild(barLabel);

        var canvasWidth = 512;
        var canvasHeight = 50;

        var canvas = document.createElement('canvas');
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;
        canvas.style.maxWidth = '100%';
        canvas.style.borderRadius = '4px';
        canvas.style.cursor = 'crosshair';
        canvas.style.display = 'block';
        canvas.className = 'grayscale-bar-canvas';

        var ctx = canvas.getContext('2d');

        // Draw gradient
        for (var x = 0; x < canvasWidth; x++) {
            var val = Math.round((x / (canvasWidth - 1)) * 255);
            ctx.fillStyle = 'rgb(' + val + ',' + val + ',' + val + ')';
            ctx.fillRect(x, 0, 1, canvasHeight);
        }

        var barWrapper = createEl('div', 'grayscale-bar-wrapper');
        barWrapper.style.position = 'relative';
        barWrapper.style.display = 'inline-block';
        barWrapper.appendChild(canvas);

        // Tooltip for value
        var tooltip = createEl('div', 'grayscale-bar-tooltip');
        tooltip.style.display = 'none';
        tooltip.style.position = 'absolute';
        tooltip.style.pointerEvents = 'none';
        tooltip.style.background = 'rgba(0,0,0,0.85)';
        tooltip.style.color = '#fff';
        tooltip.style.padding = '4px 8px';
        tooltip.style.borderRadius = '4px';
        tooltip.style.fontSize = '0.75rem';
        tooltip.style.fontFamily = 'var(--font-mono, monospace)';
        tooltip.style.zIndex = '100';
        tooltip.style.whiteSpace = 'nowrap';
        tooltip.style.top = '-28px';
        barWrapper.appendChild(tooltip);

        // Indicator line
        var indicator = createEl('div', 'grayscale-bar-indicator');
        indicator.style.display = 'none';
        indicator.style.position = 'absolute';
        indicator.style.top = '0';
        indicator.style.width = '2px';
        indicator.style.height = canvasHeight + 'px';
        indicator.style.backgroundColor = '#FFD700';
        indicator.style.pointerEvents = 'none';
        indicator.style.zIndex = '50';
        barWrapper.appendChild(indicator);

        container.appendChild(barWrapper);

        canvas.addEventListener('mousemove', function (e) {
            var rect = canvas.getBoundingClientRect();
            var scaleX = canvas.width / rect.width;
            var mx = (e.clientX - rect.left) * scaleX;
            var val = Math.round((mx / (canvasWidth - 1)) * 255);
            val = Math.max(0, Math.min(255, val));

            tooltip.textContent = 'Value: ' + val + '  (0x' + ('00' + val.toString(16).toUpperCase()).slice(-2) + ')';
            tooltip.style.display = 'block';
            var displayX = (e.clientX - barWrapper.getBoundingClientRect().left);
            tooltip.style.left = (displayX - 40) + 'px';

            indicator.style.display = 'block';
            indicator.style.left = displayX + 'px';
        });

        canvas.addEventListener('mouseleave', function () {
            tooltip.style.display = 'none';
            indicator.style.display = 'none';
        });

        // Labels: 0, 64, 128, 192, 255
        var labelsDiv = createEl('div', 'grayscale-bar-labels');
        labelsDiv.style.display = 'flex';
        labelsDiv.style.justifyContent = 'space-between';
        labelsDiv.style.maxWidth = canvasWidth + 'px';
        labelsDiv.style.fontSize = '0.7rem';
        labelsDiv.style.color = 'var(--ink-light, #666)';
        labelsDiv.style.fontFamily = 'var(--font-mono, monospace)';
        labelsDiv.style.marginTop = '4px';

        [0, 64, 128, 192, 255].forEach(function (v) {
            var span = createEl('span', null, String(v));
            labelsDiv.appendChild(span);
        });
        container.appendChild(labelsDiv);
    }

    // ========================================================================
    // 3. Pixel Arithmetic Calculator
    // ========================================================================

    function initPixelArithmetic() {
        var container = document.getElementById('arithmetic-calculator');
        var resultsContainer = document.getElementById('arithmetic-results');

        // Build the calculator UI if the container exists but is empty
        if (container && container.children.length === 0) {
            buildArithmeticCalculatorUI(container, resultsContainer);
        }

        // Also handle legacy button setup
        var legacyBtn = document.getElementById('btn-pixel-arithmetic');
        if (legacyBtn) {
            setupLegacyArithmeticButton(legacyBtn);
        }
    }

    function buildArithmeticCalculatorUI(container, resultsContainer) {
        container.textContent = '';

        var heading = createEl('h4', 'arith-heading', 'Pixel Arithmetic Calculator');
        container.appendChild(heading);

        var desc = createEl('p', 'arith-desc', 'Enter two pixel values (0-255) and see how arithmetic operations behave with uint8 overflow/underflow.');
        desc.style.fontSize = '0.85rem';
        desc.style.color = 'var(--ink-light, #666)';
        desc.style.marginBottom = '1rem';
        container.appendChild(desc);

        var form = createEl('div', 'arith-form');
        form.style.display = 'flex';
        form.style.alignItems = 'center';
        form.style.gap = '1rem';
        form.style.flexWrap = 'wrap';

        // Val1 slider
        var group1 = createEl('div', 'arith-input-group');
        var label1 = createEl('label', 'arith-label', 'Value 1:');
        label1.setAttribute('for', 'arith-range-val1');
        group1.appendChild(label1);

        var rangeVal1 = document.createElement('input');
        rangeVal1.type = 'range';
        rangeVal1.id = 'arith-range-val1';
        rangeVal1.min = '0';
        rangeVal1.max = '255';
        rangeVal1.value = '200';
        rangeVal1.className = 'arith-range';
        group1.appendChild(rangeVal1);

        var display1 = createEl('span', 'arith-display', '200');
        display1.id = 'arith-display-val1';
        display1.style.fontFamily = 'var(--font-mono, monospace)';
        display1.style.fontWeight = '600';
        display1.style.minWidth = '30px';
        display1.style.textAlign = 'center';
        group1.appendChild(display1);

        // Swatch for val1
        var swatch1 = createEl('div', 'arith-input-swatch');
        swatch1.id = 'arith-swatch-val1';
        swatch1.style.width = '24px';
        swatch1.style.height = '24px';
        swatch1.style.borderRadius = '4px';
        swatch1.style.border = '1px solid #ccc';
        swatch1.style.display = 'inline-block';
        swatch1.style.backgroundColor = 'rgb(200,200,200)';
        group1.appendChild(swatch1);
        form.appendChild(group1);

        // Val2 slider
        var group2 = createEl('div', 'arith-input-group');
        var label2 = createEl('label', 'arith-label', 'Value 2:');
        label2.setAttribute('for', 'arith-range-val2');
        group2.appendChild(label2);

        var rangeVal2 = document.createElement('input');
        rangeVal2.type = 'range';
        rangeVal2.id = 'arith-range-val2';
        rangeVal2.min = '0';
        rangeVal2.max = '255';
        rangeVal2.value = '100';
        rangeVal2.className = 'arith-range';
        group2.appendChild(rangeVal2);

        var display2 = createEl('span', 'arith-display', '100');
        display2.id = 'arith-display-val2';
        display2.style.fontFamily = 'var(--font-mono, monospace)';
        display2.style.fontWeight = '600';
        display2.style.minWidth = '30px';
        display2.style.textAlign = 'center';
        group2.appendChild(display2);

        var swatch2 = createEl('div', 'arith-input-swatch');
        swatch2.id = 'arith-swatch-val2';
        swatch2.style.width = '24px';
        swatch2.style.height = '24px';
        swatch2.style.borderRadius = '4px';
        swatch2.style.border = '1px solid #ccc';
        swatch2.style.display = 'inline-block';
        swatch2.style.backgroundColor = 'rgb(100,100,100)';
        group2.appendChild(swatch2);
        form.appendChild(group2);

        // Calculate button
        var calcBtn = createEl('button', 'btn btn-primary', 'Calculate');
        calcBtn.id = 'btn-arith-calc';
        form.appendChild(calcBtn);

        container.appendChild(form);

        // Update display on range input
        rangeVal1.addEventListener('input', function () {
            display1.textContent = rangeVal1.value;
            swatch1.style.backgroundColor = 'rgb(' + rangeVal1.value + ',' + rangeVal1.value + ',' + rangeVal1.value + ')';
        });

        rangeVal2.addEventListener('input', function () {
            display2.textContent = rangeVal2.value;
            swatch2.style.backgroundColor = 'rgb(' + rangeVal2.value + ',' + rangeVal2.value + ',' + rangeVal2.value + ')';
        });

        // Calculate handler
        calcBtn.addEventListener('click', async function () {
            var val1 = parseInt(rangeVal1.value, 10);
            var val2 = parseInt(rangeVal2.value, 10);
            await performPixelArithmetic(val1, val2, resultsContainer || container);
        });
    }

    function setupLegacyArithmeticButton(btn) {
        btn.addEventListener('click', async function () {
            var val1Input = document.getElementById('arith-val1');
            var val2Input = document.getElementById('arith-val2');
            var resultDiv = document.getElementById('pixel-arithmetic-result') || document.getElementById('arithmetic-results');

            if (!val1Input || !val2Input || !resultDiv) return;

            var val1 = parseInt(val1Input.value, 10);
            var val2 = parseInt(val2Input.value, 10);

            if (isNaN(val1) || isNaN(val2) || val1 < 0 || val1 > 255 || val2 < 0 || val2 > 255) {
                showToast('Enter valid pixel values (0-255)');
                return;
            }

            await performPixelArithmetic(val1, val2, resultDiv);
        });
    }

    async function performPixelArithmetic(val1, val2, resultDiv) {
        if (!resultDiv) return;
        resultDiv.textContent = '';
        setLoading(resultDiv, true);

        try {
            var data = await apiCall('/api/pixel-arithmetic', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ val1: val1, val2: val2 })
            });

            resultDiv.textContent = '';
            renderPixelArithmeticResults(resultDiv, val1, val2, data);
            showToast('Pixel arithmetic computed');
        } catch (e) {
            resultDiv.textContent = '';
            var errMsg = createEl('p', 'error-text', 'Failed to compute pixel arithmetic.');
            resultDiv.appendChild(errMsg);
        } finally {
            setLoading(resultDiv, false);
        }
    }

    function renderPixelArithmeticResults(container, val1, val2, data) {
        var ops = data.operations || {};

        // Build a normalized operation set from whatever the backend returns
        var operations = [
            buildArithCard('Addition', val1, val2, ops.add || ops.addition, '+',
                val1 + ' + ' + val2),
            buildArithCard('Subtraction', val1, val2, ops.subtract || ops.subtraction, '-',
                val1 + ' - ' + val2),
            buildArithCard('Absolute Difference', val1, val2, ops.absdiff || ops.absolute_difference, '|d|',
                '|' + val1 + ' - ' + val2 + '|'),
            buildArithCard('Multiplication', val1, val2, ops.multiply || ops.multiplication, 'x',
                val1 + ' x ' + val2),
            buildArithCard('Division', val1, val2, ops.divide || ops.division, '/',
                val1 + ' / ' + val2)
        ];

        var grid = createEl('div', 'arith-results-grid');
        grid.style.display = 'grid';
        grid.style.gridTemplateColumns = 'repeat(auto-fit, minmax(280px, 1fr))';
        grid.style.gap = '1rem';
        grid.style.marginTop = '1rem';

        operations.forEach(function (op) {
            var card = createEl('div', 'arith-result-card');

            // Header with operation name and possible warning
            var header = createEl('div', 'arith-result-header');
            var opName = createEl('span', 'arith-op-name', op.name);
            header.appendChild(opName);

            if (op.hasWarning) {
                var warnBadge = createEl('span', 'arith-warn-badge', op.warningText);
                header.appendChild(warnBadge);
            }
            card.appendChild(header);

            // Formula
            var formulaDiv = createEl('div', 'arith-formula', op.formula);
            card.appendChild(formulaDiv);

            // Result value
            var resultLine = createEl('div', 'arith-result-value');
            var resultLabel = createEl('span', null, 'Result: ');
            resultLabel.style.fontWeight = '500';
            resultLine.appendChild(resultLabel);
            var resultNum = createEl('span', 'arith-result-number', String(op.resultValue));
            resultNum.style.fontFamily = 'var(--font-mono, monospace)';
            resultNum.style.fontWeight = '700';
            resultNum.style.fontSize = '1.1rem';
            resultLine.appendChild(resultNum);
            card.appendChild(resultLine);

            // Explanation
            if (op.explanation) {
                var noteDiv = createEl('div', 'arith-note', op.explanation);
                card.appendChild(noteDiv);
            }

            // Intensity bar
            var barOuter = createEl('div', 'arith-bar-outer');
            var barInner = createEl('div', 'arith-bar-inner');
            var pct = (clamp255(op.resultValue) / 255) * 100;
            barInner.style.width = pct.toFixed(1) + '%';
            var intensity = clamp255(op.resultValue);
            barInner.style.backgroundColor = 'rgb(' + intensity + ',' + intensity + ',' + intensity + ')';
            barOuter.appendChild(barInner);

            var barLabel = createEl('span', 'arith-bar-label', clamp255(op.resultValue) + ' / 255');
            barOuter.appendChild(barLabel);
            card.appendChild(barOuter);

            // Color swatch row
            var swatchRow = createEl('div', 'arith-swatch-row');
            var sw1 = createEl('div', 'arith-swatch');
            sw1.style.backgroundColor = 'rgb(' + val1 + ',' + val1 + ',' + val1 + ')';
            sw1.title = 'Value 1: ' + val1;
            swatchRow.appendChild(sw1);

            var opSymbol = createEl('span', 'arith-op-symbol', op.symbol);
            swatchRow.appendChild(opSymbol);

            var sw2 = createEl('div', 'arith-swatch');
            sw2.style.backgroundColor = 'rgb(' + val2 + ',' + val2 + ',' + val2 + ')';
            sw2.title = 'Value 2: ' + val2;
            swatchRow.appendChild(sw2);

            var eqSign = createEl('span', 'arith-op-symbol', '=');
            swatchRow.appendChild(eqSign);

            var swResult = createEl('div', 'arith-swatch');
            var rv = clamp255(op.resultValue);
            swResult.style.backgroundColor = 'rgb(' + rv + ',' + rv + ',' + rv + ')';
            swResult.title = 'Result: ' + rv;
            swatchRow.appendChild(swResult);

            card.appendChild(swatchRow);
            grid.appendChild(card);
        });

        container.appendChild(grid);
    }

    function buildArithCard(name, val1, val2, opData, symbol, formulaPrefix) {
        var result = {
            name: name,
            symbol: symbol,
            formula: formulaPrefix,
            resultValue: 0,
            explanation: '',
            hasWarning: false,
            warningText: ''
        };

        if (opData) {
            // API returns {result, saturated, explanation} or similar
            var resVal = opData.result !== undefined ? opData.result : opData.saturated;
            if (resVal === undefined) resVal = opData.scaled;
            if (resVal === undefined) resVal = 0;

            result.resultValue = resVal;
            result.explanation = opData.explanation || '';
            result.formula = formulaPrefix + ' = ' + resVal;

            // Check for overflow/underflow indicators
            if (opData.saturated !== undefined && opData.result !== undefined && opData.result !== opData.saturated) {
                result.hasWarning = true;
                result.warningText = name === 'Subtraction' ? 'Underflow' : 'Overflow';
            }
            // Also check if explanation mentions overflow/underflow
            if (result.explanation && (result.explanation.toLowerCase().indexOf('overflow') !== -1 ||
                result.explanation.toLowerCase().indexOf('underflow') !== -1 ||
                result.explanation.toLowerCase().indexOf('saturate') !== -1 ||
                result.explanation.toLowerCase().indexOf('clamp') !== -1 ||
                result.explanation.toLowerCase().indexOf('wraps') !== -1)) {
                result.hasWarning = true;
                if (!result.warningText) {
                    if (result.explanation.toLowerCase().indexOf('underflow') !== -1) {
                        result.warningText = 'Underflow';
                    } else {
                        result.warningText = 'Overflow';
                    }
                }
            }
        } else {
            // Fallback: compute locally
            var raw;
            switch (name) {
                case 'Addition':
                    raw = val1 + val2;
                    result.resultValue = Math.min(raw, 255);
                    result.formula = formulaPrefix + ' = ' + raw;
                    if (raw > 255) {
                        result.hasWarning = true;
                        result.warningText = 'Overflow';
                        result.explanation = 'Raw sum ' + raw + ' exceeds 255, saturated to ' + result.resultValue + '.';
                    } else {
                        result.explanation = 'No overflow. Result within [0, 255].';
                    }
                    break;
                case 'Subtraction':
                    raw = val1 - val2;
                    result.resultValue = Math.max(raw, 0);
                    result.formula = formulaPrefix + ' = ' + raw;
                    if (raw < 0) {
                        result.hasWarning = true;
                        result.warningText = 'Underflow';
                        result.explanation = 'Raw result ' + raw + ' is negative, clamped to 0. uint8 wrapping: ' + ((raw % 256 + 256) % 256) + '.';
                    } else {
                        result.explanation = 'No underflow. Result within [0, 255].';
                    }
                    break;
                case 'Absolute Difference':
                    result.resultValue = Math.abs(val1 - val2);
                    result.formula = formulaPrefix + ' = ' + result.resultValue;
                    result.explanation = 'Always non-negative, never overflows/underflows.';
                    break;
                case 'Multiplication':
                    raw = val1 * val2;
                    result.resultValue = Math.min(Math.round(raw / 255), 255);
                    result.formula = '(' + val1 + ' x ' + val2 + ') / 255 = ' + result.resultValue;
                    result.explanation = 'Raw product: ' + raw + '. Scaled by dividing by 255.';
                    break;
                case 'Division':
                    if (val2 !== 0) {
                        result.resultValue = Math.min(Math.round(val1 / val2), 255);
                        result.formula = formulaPrefix + ' = ' + result.resultValue;
                        result.explanation = 'Raw quotient: ' + (val1 / val2).toFixed(4) + '.';
                    } else {
                        result.resultValue = 255;
                        result.formula = val1 + ' / 0 = undefined';
                        result.explanation = 'Division by zero is undefined.';
                    }
                    break;
            }
        }

        return result;
    }

    // ========================================================================
    // 4. Bit Depth Comparison
    // ========================================================================

    function initBitDepth() {
        var container = document.getElementById('bit-depth-container');
        var legacyBtn = document.getElementById('btn-bit-depth');

        // If we have the new container, build UI inside it
        if (container) {
            buildBitDepthUI(container);
        }

        // Also handle legacy button if present
        if (legacyBtn && !container) {
            setupLegacyBitDepthButton(legacyBtn);
        }
    }

    function populateBitDepthSelector() {
        var select = document.getElementById('bit-depth-image-select');
        if (!select || availableImages.length === 0) return;

        select.textContent = '';
        availableImages.forEach(function (img) {
            var opt = document.createElement('option');
            opt.value = img.filename;
            opt.textContent = img.display_name + ' (' + img.width + 'x' + img.height + ')';
            select.appendChild(opt);
        });
    }

    function buildBitDepthUI(container) {
        container.textContent = '';

        var heading = createEl('h4', 'bit-depth-section-heading', 'Bit Depth Comparison');
        container.appendChild(heading);

        var desc = createEl('p', 'bit-depth-section-desc', 'Select an image and see how reducing bit depth affects visual quality. Fewer bits = fewer gray levels = visible contouring artifacts.');
        desc.style.fontSize = '0.85rem';
        desc.style.color = 'var(--ink-light, #666)';
        desc.style.marginBottom = '1rem';
        container.appendChild(desc);

        var controls = createEl('div', 'bit-depth-controls');
        controls.style.display = 'flex';
        controls.style.gap = '1rem';
        controls.style.alignItems = 'center';
        controls.style.flexWrap = 'wrap';
        controls.style.marginBottom = '1rem';

        var selectLabel = createEl('label', null, 'Image:');
        selectLabel.setAttribute('for', 'bit-depth-image-select');
        selectLabel.style.fontWeight = '500';
        controls.appendChild(selectLabel);

        var select = document.createElement('select');
        select.id = 'bit-depth-image-select';
        select.className = 'bit-depth-select';
        // Will be populated after images load
        var defaultOpt = document.createElement('option');
        defaultOpt.value = '';
        defaultOpt.textContent = 'Loading images...';
        select.appendChild(defaultOpt);
        controls.appendChild(select);

        var btn = createEl('button', 'btn btn-primary', 'Show Bit Depth Comparison');
        btn.id = 'btn-bit-depth-show';
        controls.appendChild(btn);

        container.appendChild(controls);

        var resultDiv = createEl('div', 'bit-depth-result');
        resultDiv.id = 'bit-depth-display-result';
        container.appendChild(resultDiv);

        btn.addEventListener('click', async function () {
            var filename = select.value;
            if (!filename) {
                showToast('Select an image first');
                return;
            }
            await fetchAndRenderBitDepth(filename, resultDiv);
        });

        // If images are already loaded, populate
        if (availableImages.length > 0) {
            populateBitDepthSelector();
        }
    }

    function setupLegacyBitDepthButton(btn) {
        btn.addEventListener('click', async function () {
            var resultDiv = document.getElementById('bit-depth-result');
            if (!resultDiv) return;

            var filename = '';
            if (availableImages.length > 0) {
                filename = availableImages[0].filename;
            } else {
                showToast('No images loaded yet');
                return;
            }
            await fetchAndRenderBitDepth(filename, resultDiv);
        });
    }

    async function fetchAndRenderBitDepth(filename, resultDiv) {
        resultDiv.textContent = '';
        setLoading(resultDiv, true);

        try {
            var data = await apiCall('/api/bit-depth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: filename })
            });

            resultDiv.textContent = '';
            var normalized = { filename: filename };
            var imgs = data.images || data;
            if (imgs['8_bit']) normalized.bit_8 = imgs['8_bit'];
            if (imgs['4_bit']) normalized.bit_4 = imgs['4_bit'];
            if (imgs['2_bit']) normalized.bit_2 = imgs['2_bit'];
            if (imgs['1_bit']) normalized.bit_1 = imgs['1_bit'];
            if (imgs.bit_8) normalized.bit_8 = imgs.bit_8;
            if (imgs.bit_4) normalized.bit_4 = imgs.bit_4;
            if (imgs.bit_2) normalized.bit_2 = imgs.bit_2;
            if (imgs.bit_1) normalized.bit_1 = imgs.bit_1;
            renderBitDepthComparison(resultDiv, normalized);
            showToast('Bit depth comparison generated');
        } catch (e) {
            resultDiv.textContent = '';
            var errMsg = createEl('p', 'error-text', 'Failed to generate bit depth comparison.');
            resultDiv.appendChild(errMsg);
        } finally {
            setLoading(resultDiv, false);
        }
    }

    function renderBitDepthComparison(container, data) {
        var heading = createEl('h4', 'bit-depth-heading', 'Bit Depth Quantization: ' + (data.filename || 'Image'));
        container.appendChild(heading);

        var desc = createEl('p', 'bit-depth-desc',
            'Reducing intensity resolution (quantization levels) from 8-bit (256 levels) down to 1-bit (2 levels) ' +
            'demonstrates the effect of bit depth on image quality. Fewer bits result in visible false contouring artifacts.');
        container.appendChild(desc);

        var grid = createEl('div', 'bit-depth-grid');

        var bitDepths = [
            { key: 'bit_8', label: '8-bit (256 levels)', bits: 8 },
            { key: 'bit_4', label: '4-bit (16 levels)', bits: 4 },
            { key: 'bit_2', label: '2-bit (4 levels)', bits: 2 },
            { key: 'bit_1', label: '1-bit (2 levels)', bits: 1 }
        ];

        bitDepths.forEach(function (bd) {
            if (!data[bd.key]) return;

            var card = createEl('div', 'bit-depth-card');

            var imgEl = document.createElement('img');
            imgEl.src = 'data:image/png;base64,' + data[bd.key];
            imgEl.alt = bd.label;
            imgEl.className = 'bit-depth-img';
            card.appendChild(imgEl);

            var labelDiv = createEl('div', 'bit-depth-label', bd.label);
            card.appendChild(labelDiv);

            var infoDiv = createEl('div', 'bit-depth-info');
            var formula = createEl('span', 'bit-depth-formula', 'L = 2^' + bd.bits + ' = ' + Math.pow(2, bd.bits) + ' levels');
            infoDiv.appendChild(formula);
            card.appendChild(infoDiv);

            grid.appendChild(card);
        });

        container.appendChild(grid);
    }

    // ========================================================================
    // 5. Step-by-Step Pipeline
    // ========================================================================

    function initStepByStep() {
        var btn = document.getElementById('btn-step-by-step');
        if (!btn) return;

        btn.addEventListener('click', async function () {
            var resultDiv = document.getElementById('step-by-step-container')
                || document.getElementById('step-by-step-result');
            if (!resultDiv) return;

            resultDiv.textContent = '';
            setLoading(resultDiv, true);

            // Use current pair or first recommended pair
            var image1, image2;
            if (currentPair) {
                image1 = currentPair.image1;
                image2 = currentPair.image2;
            } else if (recommendedPairs.length > 0) {
                image1 = recommendedPairs[0].image1;
                image2 = recommendedPairs[0].image2;
            } else if (availableImages.length >= 2) {
                image1 = availableImages[0].filename;
                image2 = availableImages[1].filename;
            } else {
                showToast('No image pair available');
                setLoading(resultDiv, false);
                return;
            }

            try {
                var data = await apiCall('/api/step-by-step', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ image1: image1, image2: image2 })
                });

                resultDiv.textContent = '';
                setLoading(resultDiv, false);

                if (data.steps && data.steps.length > 0) {
                    var normalizedSteps = normalizeSteps(data.steps);
                    renderStepByStep(resultDiv, normalizedSteps);
                }
                showToast('Step-by-step pipeline loaded');
            } catch (e) {
                setLoading(resultDiv, false);
                resultDiv.textContent = '';
                var errMsg = createEl('p', 'error-text', 'Failed to load step-by-step pipeline.');
                resultDiv.appendChild(errMsg);
            }
        });
    }

    /**
     * Normalize backend step-by-step response.
     */
    function normalizeSteps(rawSteps) {
        return rawSteps.map(function (s) {
            var result = {
                step_number: s.step || s.step_number || 0,
                title: s.title || '',
                explanation: s.what_happened || s.explanation || '',
                code: s.code || null
            };

            var data = s.data || {};

            // Look for pixel grids
            if (data.sample_img1_5x5) {
                result.pixel_grid = data.sample_img1_5x5;
                result.grid_title = 'Image 1 sample (5x5 center)';
            } else if (data.sample_5x5_center) {
                result.pixel_grid = data.sample_5x5_center;
                result.grid_title = 'Sample (5x5 center)';
            } else if (data.image1 && data.image1.sample_5x5_center) {
                result.pixel_grid = data.image1.sample_5x5_center;
                result.grid_title = 'Image 1 sample (5x5 center)';
            }

            // Look for stats
            var statsObj = {};
            var hasStats = false;
            Object.keys(data).forEach(function (key) {
                var val = data[key];
                if (typeof val === 'number' || typeof val === 'string') {
                    statsObj[key] = val;
                    hasStats = true;
                } else if (typeof val === 'boolean') {
                    statsObj[key] = val ? 'Yes' : 'No';
                    hasStats = true;
                } else if (Array.isArray(val) && val.length <= 4 && typeof val[0] === 'number') {
                    statsObj[key] = val.join(' x ');
                    hasStats = true;
                }
            });
            if (hasStats) {
                result.stats = statsObj;
            }

            // Look for base64 images
            if (data.diff_image) {
                result.image = data.diff_image;
            } else if (data.enhanced_image) {
                result.image = data.enhanced_image;
            }

            return result;
        });
    }

    function renderStepByStep(container, steps) {
        var timeline = createEl('div', 'step-timeline');
        container.appendChild(timeline);

        steps.forEach(function (step, index) {
            setTimeout(function () {
                var card = createEl('div', 'step-card');
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

                // Step header with circle number
                var header = createEl('div', 'step-header');

                var stepCircle = createEl('div', 'step-circle');
                var stepNum = createEl('span', 'step-number', String(step.step_number));
                stepCircle.appendChild(stepNum);
                stepCircle.style.width = '36px';
                stepCircle.style.height = '36px';
                stepCircle.style.borderRadius = '50%';
                stepCircle.style.backgroundColor = 'var(--gold, #d4a030)';
                stepCircle.style.color = '#fff';
                stepCircle.style.display = 'flex';
                stepCircle.style.alignItems = 'center';
                stepCircle.style.justifyContent = 'center';
                stepCircle.style.fontWeight = '700';
                stepCircle.style.flexShrink = '0';
                header.appendChild(stepCircle);

                var stepTitle = createEl('span', 'step-title', step.title);
                header.appendChild(stepTitle);

                var expandIcon = createEl('span', 'step-expand-icon', '+');
                header.appendChild(expandIcon);
                card.appendChild(header);

                // Expandable body
                var body = createEl('div', 'step-body');
                body.style.display = 'none';

                // Explanation
                if (step.explanation) {
                    var explainSection = createEl('div', 'step-section');
                    var explainLabel = createEl('h5', 'step-section-label', 'What happened');
                    explainSection.appendChild(explainLabel);
                    var explainText = createEl('p', 'step-explanation', step.explanation);
                    explainSection.appendChild(explainText);
                    body.appendChild(explainSection);
                }

                // Code snippet
                if (step.code) {
                    var codeSection = createEl('div', 'step-section');
                    var codeLabel = createEl('h5', 'step-section-label', 'Python Code');
                    codeSection.appendChild(codeLabel);
                    var pre = createEl('pre', 'step-code');
                    var code = createEl('code', null, step.code);
                    pre.appendChild(code);
                    codeSection.appendChild(pre);
                    body.appendChild(codeSection);
                }

                // Pixel grid visualization
                if (step.pixel_grid) {
                    var gridSection = createEl('div', 'step-section');
                    var gridLabel = createEl('h5', 'step-section-label', 'Pixel Data (sample)');
                    gridSection.appendChild(gridLabel);
                    var pixTable = createPixelTable(step.pixel_grid, step.grid_title || null);
                    gridSection.appendChild(pixTable);
                    body.appendChild(gridSection);
                }

                // Stats
                if (step.stats) {
                    var statsSection = createEl('div', 'step-section');
                    var statsLabel = createEl('h5', 'step-section-label', 'Statistics');
                    statsSection.appendChild(statsLabel);
                    var statsGrid = createEl('div', 'step-stats-grid');
                    Object.keys(step.stats).forEach(function (key) {
                        var statItem = createEl('div', 'step-stat-item');
                        var statKey = createEl('span', 'step-stat-key', key.replace(/_/g, ' '));
                        statItem.appendChild(statKey);
                        var statVal = createEl('span', 'step-stat-val', String(step.stats[key]));
                        statItem.appendChild(statVal);
                        statsGrid.appendChild(statItem);
                    });
                    statsSection.appendChild(statsGrid);
                    body.appendChild(statsSection);
                }

                // Image (base64)
                if (step.image) {
                    var imgSection = createEl('div', 'step-section');
                    var imgEl = document.createElement('img');
                    imgEl.src = 'data:image/png;base64,' + step.image;
                    imgEl.alt = step.title;
                    imgEl.className = 'step-image';
                    imgSection.appendChild(imgEl);
                    body.appendChild(imgSection);
                }

                card.appendChild(body);

                // Toggle expand/collapse
                header.addEventListener('click', function () {
                    var isExpanded = body.style.display !== 'none';
                    body.style.display = isExpanded ? 'none' : 'block';
                    expandIcon.textContent = isExpanded ? '+' : '-';
                    header.classList.toggle('expanded', !isExpanded);
                });

                timeline.appendChild(card);

                // Trigger staggered fade-in animation
                requestAnimationFrame(function () {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                });

            }, index * 250);
        });
    }

    // ========================================================================
    // 6. Surface Plot
    // ========================================================================

    function initSurfacePlot() {
        var btn = document.getElementById('btn-surface-plot');
        if (!btn) return;

        btn.addEventListener('click', async function () {
            var resultDiv = document.getElementById('surface-plot-container')
                || document.getElementById('surface-plot-result');
            if (!resultDiv) return;

            resultDiv.textContent = '';
            setLoading(resultDiv, true);

            var filename = lastDiffFilename;
            if (!filename && availableImages.length > 0) {
                filename = availableImages[0].filename;
            }
            if (!filename) {
                showToast('No image available for surface plot');
                setLoading(resultDiv, false);
                return;
            }

            var x = 0;
            var y = 0;
            var size = 64;

            try {
                var data = await apiCall('/api/surface-plot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: filename, x: x, y: y, size: size })
                });

                resultDiv.textContent = '';

                var plotDesc = createEl('p', 'surface-plot-desc',
                    '3D surface plot showing pixel intensity values as elevation. ' +
                    'Higher peaks correspond to brighter pixels. Region: (' + x + ',' + y + ') to (' + (x + size) + ',' + (y + size) + ').');
                resultDiv.appendChild(plotDesc);

                if (data.plot) {
                    var imgEl = document.createElement('img');
                    imgEl.src = 'data:image/png;base64,' + data.plot;
                    imgEl.alt = '3D Surface Plot';
                    imgEl.className = 'surface-plot-img';
                    resultDiv.appendChild(imgEl);
                }

                showToast('3D surface plot generated');
            } catch (e) {
                resultDiv.textContent = '';
                var errMsg = createEl('p', 'error-text', 'Failed to generate surface plot.');
                resultDiv.appendChild(errMsg);
            } finally {
                setLoading(resultDiv, false);
            }
        });
    }

    // ========================================================================
    // 7. Quiz System
    // ========================================================================

    function initQuizzes() {
        // Render quizzes into their designated containers
        renderQuizIntoContainer('quiz-foundations', QUIZ_DATA.foundations);
        renderQuizIntoContainer('quiz-practical1', QUIZ_DATA.practical1);

        // Also handle pre-existing quiz containers that already have questions in the HTML
        initPrebuiltQuizzes();
    }

    function renderQuizIntoContainer(containerId, questions) {
        var container = document.getElementById(containerId);
        if (!container || !questions || questions.length === 0) return;

        // Only render if the container is empty (don't overwrite pre-built quizzes)
        if (container.children.length > 0) return;

        var heading = createEl('h4', 'quiz-heading', containerId === 'quiz-foundations' ? 'Foundations Quiz' : 'Practical 1 Quiz');
        container.appendChild(heading);

        var score = { correct: 0, answered: 0, total: questions.length };

        // Score display
        var scoreDisplay = createEl('div', 'quiz-score');
        var scoreText = createEl('span', 'quiz-score-text', 'Score: 0 / ' + score.total);
        scoreDisplay.appendChild(scoreText);
        var progressBar = createEl('div', 'quiz-progress-bar');
        progressBar.style.height = '6px';
        progressBar.style.backgroundColor = 'var(--cream-dark, #e0d5c0)';
        progressBar.style.borderRadius = '3px';
        progressBar.style.overflow = 'hidden';
        progressBar.style.marginTop = '6px';
        var progressFill = createEl('div', 'quiz-progress-fill');
        progressFill.style.height = '100%';
        progressFill.style.width = '0%';
        progressFill.style.backgroundColor = 'var(--green-felt, #2e7d32)';
        progressFill.style.transition = 'width 0.4s ease, background-color 0.4s ease';
        progressBar.appendChild(progressFill);
        scoreDisplay.appendChild(progressBar);
        container.appendChild(scoreDisplay);

        questions.forEach(function (q, qIndex) {
            var questionCard = createEl('div', 'quiz-question');

            // Question number and text
            var qNum = createEl('div', 'quiz-question-number', 'Q' + (qIndex + 1) + '.');
            qNum.style.fontWeight = '700';
            qNum.style.color = 'var(--gold, #d4a030)';
            qNum.style.marginBottom = '4px';
            questionCard.appendChild(qNum);

            var qText = createEl('p', 'quiz-question-text', q.question);
            qText.style.fontWeight = '500';
            qText.style.marginBottom = '0.8rem';
            questionCard.appendChild(qText);

            // Options
            var optionsDiv = createEl('div', 'quiz-options');
            var isAnswered = false;

            q.options.forEach(function (optText, optIndex) {
                var optBtn = createEl('button', 'quiz-option', optText);
                optBtn.dataset.correct = String(optIndex === q.correct);
                optBtn.style.display = 'block';
                optBtn.style.width = '100%';
                optBtn.style.textAlign = 'left';
                optBtn.style.padding = '0.6rem 1rem';
                optBtn.style.marginBottom = '0.4rem';
                optBtn.style.border = '1px solid var(--cream-dark, #e0d5c0)';
                optBtn.style.borderRadius = '6px';
                optBtn.style.cursor = 'pointer';
                optBtn.style.backgroundColor = 'var(--cream, #f5f0e8)';
                optBtn.style.fontFamily = 'inherit';
                optBtn.style.fontSize = '0.85rem';
                optBtn.style.transition = 'background-color 0.3s ease, border-color 0.3s ease';

                optBtn.addEventListener('click', function () {
                    if (isAnswered) return;
                    isAnswered = true;
                    score.answered++;

                    var isCorrect = optIndex === q.correct;

                    if (isCorrect) {
                        score.correct++;
                        optBtn.classList.add('correct');
                        optBtn.style.backgroundColor = '#c8e6c9';
                        optBtn.style.borderColor = '#2e7d32';
                    } else {
                        optBtn.classList.add('incorrect');
                        optBtn.style.backgroundColor = '#ffcdd2';
                        optBtn.style.borderColor = '#c62828';

                        // Highlight correct answer
                        var allOpts = optionsDiv.querySelectorAll('.quiz-option');
                        allOpts.forEach(function (opt) {
                            if (opt.dataset.correct === 'true') {
                                opt.classList.add('correct');
                                opt.style.backgroundColor = '#c8e6c9';
                                opt.style.borderColor = '#2e7d32';
                            }
                        });
                    }

                    // Disable all options
                    optionsDiv.querySelectorAll('.quiz-option').forEach(function (opt) {
                        opt.style.cursor = 'default';
                        opt.style.opacity = '0.85';
                    });

                    // Show explanation
                    explanationDiv.style.display = 'block';

                    // Update score
                    scoreText.textContent = 'Score: ' + score.correct + ' / ' + score.total;
                    progressFill.style.width = ((score.answered / score.total) * 100) + '%';
                    progressFill.style.backgroundColor = score.correct === score.answered ? 'var(--green-felt, #2e7d32)' : 'var(--gold, #d4a030)';

                    // Show final result
                    if (score.answered === score.total) {
                        showQuizResult(container, score.correct, score.total);
                    }
                });

                optionsDiv.appendChild(optBtn);
            });
            questionCard.appendChild(optionsDiv);

            // Explanation (hidden until answered)
            var explanationDiv = createEl('div', 'quiz-explanation', q.explanation);
            explanationDiv.style.display = 'none';
            explanationDiv.style.marginTop = '0.8rem';
            explanationDiv.style.padding = '0.8rem';
            explanationDiv.style.backgroundColor = 'var(--cream-light, #faf7f2)';
            explanationDiv.style.borderLeft = '3px solid var(--gold, #d4a030)';
            explanationDiv.style.borderRadius = '0 6px 6px 0';
            explanationDiv.style.fontSize = '0.85rem';
            explanationDiv.style.lineHeight = '1.5';
            questionCard.appendChild(explanationDiv);

            container.appendChild(questionCard);
        });
    }

    function initPrebuiltQuizzes() {
        // Handle quiz containers that already have .quiz-question elements from HTML
        var quizContainers = document.querySelectorAll('.quiz-container');
        quizContainers.forEach(function (quizContainer) {
            var questions = quizContainer.querySelectorAll('.quiz-question');
            if (questions.length === 0) return;

            var totalQuestions = questions.length;
            var score = 0;
            var answered = 0;

            // Score display
            var scoreDisplay = createEl('div', 'quiz-score');
            var scoreText = createEl('span', 'quiz-score-text', 'Score: 0 / ' + totalQuestions);
            scoreDisplay.appendChild(scoreText);
            var progressBar = createEl('div', 'quiz-progress-bar');
            progressBar.style.height = '6px';
            progressBar.style.backgroundColor = 'var(--cream-dark, #e0d5c0)';
            progressBar.style.borderRadius = '3px';
            progressBar.style.overflow = 'hidden';
            progressBar.style.marginTop = '6px';
            var progressFill = createEl('div', 'quiz-progress-fill');
            progressFill.style.height = '100%';
            progressFill.style.width = '0%';
            progressFill.style.backgroundColor = 'var(--green-felt, #2e7d32)';
            progressFill.style.transition = 'width 0.4s ease, background-color 0.4s ease';
            progressBar.appendChild(progressFill);
            scoreDisplay.appendChild(progressBar);

            if (questions.length > 0) {
                quizContainer.insertBefore(scoreDisplay, questions[0]);
            }

            questions.forEach(function (questionEl) {
                var options = questionEl.querySelectorAll('.quiz-option');
                var explanationEl = questionEl.querySelector('.quiz-explanation');
                var isAnswered = false;

                options.forEach(function (option) {
                    option.addEventListener('click', function () {
                        if (isAnswered) return;
                        isAnswered = true;
                        answered++;

                        var isCorrect = option.dataset.correct === 'true';

                        if (isCorrect) {
                            score++;
                            option.classList.add('quiz-option-correct');
                        } else {
                            option.classList.add('quiz-option-wrong');
                            options.forEach(function (opt) {
                                if (opt.dataset.correct === 'true') {
                                    opt.classList.add('quiz-option-correct');
                                }
                            });
                        }

                        options.forEach(function (opt) {
                            opt.classList.add('quiz-option-disabled');
                        });

                        if (explanationEl) {
                            explanationEl.style.display = 'block';
                        }

                        scoreText.textContent = 'Score: ' + score + ' / ' + totalQuestions;
                        progressFill.style.width = ((answered / totalQuestions) * 100) + '%';
                        progressFill.style.backgroundColor = score === answered ? 'var(--green-felt, #2e7d32)' : 'var(--gold, #d4a030)';

                        if (answered === totalQuestions) {
                            showQuizResult(quizContainer, score, totalQuestions);
                        }
                    });
                });
            });
        });
    }

    function showQuizResult(quizContainer, score, total) {
        var resultDiv = createEl('div', 'quiz-final-result');
        resultDiv.style.marginTop = '1.5rem';
        resultDiv.style.padding = '1.5rem';
        resultDiv.style.borderRadius = '8px';
        resultDiv.style.textAlign = 'center';

        var pct = Math.round((score / total) * 100);
        var grade;
        if (pct >= 90) {
            grade = 'Excellent!';
            resultDiv.style.backgroundColor = '#c8e6c9';
            resultDiv.style.borderLeft = '4px solid #2e7d32';
        } else if (pct >= 70) {
            grade = 'Good job!';
            resultDiv.style.backgroundColor = '#fff9c4';
            resultDiv.style.borderLeft = '4px solid #f9a825';
        } else if (pct >= 50) {
            grade = 'Keep studying!';
            resultDiv.style.backgroundColor = '#ffe0b2';
            resultDiv.style.borderLeft = '4px solid #ef6c00';
        } else {
            grade = 'Review the material.';
            resultDiv.style.backgroundColor = '#ffcdd2';
            resultDiv.style.borderLeft = '4px solid #c62828';
        }

        var resultTitle = createEl('h4', 'quiz-result-title', 'Quiz Complete!');
        resultTitle.style.marginBottom = '0.5rem';
        resultDiv.appendChild(resultTitle);

        var resultScore = createEl('div', 'quiz-result-score', score + ' / ' + total + ' (' + pct + '%)');
        resultScore.style.fontSize = '1.3rem';
        resultScore.style.fontWeight = '700';
        resultScore.style.marginBottom = '0.5rem';
        resultDiv.appendChild(resultScore);

        var resultGrade = createEl('div', 'quiz-result-grade', grade);
        resultGrade.style.fontSize = '1.1rem';
        resultDiv.appendChild(resultGrade);

        quizContainer.appendChild(resultDiv);
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // ========================================================================
    // Pixel Inspector on Click
    // ========================================================================

    function initPixelInspector() {
        var resultImages = ['result-img1', 'result-img2', 'result-diff', 'result-diff-enhanced'];
        resultImages.forEach(function (imgId) {
            var imgEl = document.getElementById(imgId);
            if (!imgEl) return;

            imgEl.style.cursor = 'crosshair';
            imgEl.title = 'Click to inspect pixel values at this location';

            imgEl.addEventListener('click', function (e) {
                if (!imgEl.src || imgEl.src === '') return;
                handlePixelInspectorClick(e, imgEl);
            });
        });
    }

    function handlePixelInspectorClick(e, imgEl) {
        var rect = imgEl.getBoundingClientRect();
        var clickX = e.clientX - rect.left;
        var clickY = e.clientY - rect.top;

        var scaleX = imgEl.naturalWidth / rect.width;
        var scaleY = imgEl.naturalHeight / rect.height;
        var pixelX = Math.round(clickX * scaleX);
        var pixelY = Math.round(clickY * scaleY);

        var container = document.getElementById('result-container');
        if (!container) return;
        var filename = '';
        if (imgEl.id === 'result-img1') {
            filename = container.dataset.img1 || '';
        } else if (imgEl.id === 'result-img2') {
            filename = container.dataset.img2 || '';
        } else if (imgEl.id === 'result-diff' || imgEl.id === 'result-diff-enhanced') {
            filename = container.dataset.img1 || '';
        }

        if (!filename) {
            showToast('No image data available for inspection');
            return;
        }

        fetchPixelView(filename, pixelX, pixelY, imgEl);
    }

    async function fetchPixelView(filename, x, y, anchorEl) {
        try {
            var data = await apiCall('/api/pixel-view', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: filename, x: x, y: y, size: 9 })
            });

            if (data && (data.pixel_grid || data.grid)) {
                showPixelInspectorPopup(data.pixel_grid || data.grid, x, y, anchorEl);
            }
        } catch (e) {
            // The toast from apiCall is sufficient
        }
    }

    function showPixelInspectorPopup(grid, x, y, anchorEl) {
        var existing = document.querySelector('.pixel-inspector-popup');
        if (existing) existing.remove();

        var popup = createEl('div', 'pixel-inspector-popup');

        var title = createEl('div', 'pixel-inspector-title', 'Pixel Region at (' + x + ', ' + y + ')');
        popup.appendChild(title);

        var tableWrapper = createPixelTable(grid, null);
        popup.appendChild(tableWrapper);

        var closeBtn = createEl('button', 'pixel-inspector-close', 'Close');
        closeBtn.addEventListener('click', function () { popup.remove(); });
        popup.appendChild(closeBtn);

        var card = anchorEl.closest('.result-image-card');
        if (card) {
            card.style.position = 'relative';
            card.appendChild(popup);
        } else {
            document.body.appendChild(popup);
        }
    }

    // ========================================================================
    // Event Listeners
    // ========================================================================
    function bindEvents() {
        var btnCompute = document.getElementById('btn-compute-custom');
        if (btnCompute) {
            btnCompute.addEventListener('click', computeCustomPair);
        }

        var btnHist1 = document.getElementById('btn-histogram-1');
        if (btnHist1) {
            btnHist1.addEventListener('click', function () {
                generateHistogram('select-img1');
            });
        }

        var btnHist2 = document.getElementById('btn-histogram-2');
        if (btnHist2) {
            btnHist2.addEventListener('click', function () {
                generateHistogram('select-img2');
            });
        }

        var btnFullPlot = document.getElementById('btn-full-plot');
        if (btnFullPlot) {
            btnFullPlot.addEventListener('click', generateFullPlot);
        }

        var btnLoadDemos = document.getElementById('btn-load-demos');
        if (btnLoadDemos) {
            btnLoadDemos.addEventListener('click', loadMatplotlibDemos);
        }
    }

    // ========================================================================
    // Init
    // ========================================================================
    async function init() {
        initTabs();
        initNav();
        bindEvents();
        initPixelArithmetic();
        initStepByStep();
        initBitDepth();
        initSurfacePlot();
        initPixelInspector();
        initQuizzes();
        initPixelGrid();
        initGrayscaleBar();
        initSectionReveal();
        initAnimatedCounters();

        await Promise.all([
            loadImages(),
            loadMatplotlibReference()
        ]);

        // After images are loaded, update pixel grid with real data and populate bit depth selector
        attemptLoadPixelGridFromImage();
        populateBitDepthSelector();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
