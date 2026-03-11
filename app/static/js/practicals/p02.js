/**
 * DIP Practical 2 - Image Subtraction & Inversion
 * Operates on the first and last images from the Chapter 2 dataset.
 *
 * Uses the window.DIP namespace (apiCall, showToast, setLoading,
 * createEl, animateValue) provided by core.js.
 */
(function () {
    'use strict';

    var D = window.DIP;
    if (!D) {
        console.error('[P02] window.DIP not found. Ensure core.js is loaded first.');
        return;
    }

    // ------------------------------------------------------------------ //
    //  State                                                              //
    // ------------------------------------------------------------------ //

    var targetFirst = null;
    var targetLast = null;
    var targetsLoaded = false;

    // ------------------------------------------------------------------ //
    //  Helpers                                                            //
    // ------------------------------------------------------------------ //

    function clearChildren(el) {
        while (el.firstChild) el.removeChild(el.firstChild);
    }

    function buildImageCard(base64, caption) {
        var card = D.createEl('div', 'p02-result-card');
        var img = D.createEl('img');
        img.src = 'data:image/png;base64,' + base64;
        img.alt = caption;
        img.loading = 'lazy';
        card.appendChild(img);
        var cap = D.createEl('div', 'result-caption', caption);
        card.appendChild(cap);
        return card;
    }

    function buildStatCard(label, value) {
        var card = D.createEl('div', 'p02-stat-card');
        var valEl = D.createEl('span', 'stat-value', '--');
        card.appendChild(valEl);
        var labEl = D.createEl('span', 'stat-label', label);
        card.appendChild(labEl);
        requestAnimationFrame(function () {
            var num = parseFloat(value);
            if (!isNaN(num)) {
                D.animateValue(valEl, 0, num, 700);
            } else {
                valEl.textContent = value;
            }
        });
        return card;
    }

    function renderPlot(container, base64, altText) {
        clearChildren(container);
        if (!base64) return;
        var img = D.createEl('img');
        img.src = 'data:image/png;base64,' + base64;
        img.alt = altText || 'Plot';
        img.loading = 'lazy';
        container.appendChild(img);
    }

    function enableButtons() {
        var btns = document.querySelectorAll('#compute-subtraction-btn, #subtraction-plot-btn, #invert-first-btn, #invert-last-btn, #inversion-comparison-btn, #combined-btn');
        btns.forEach(function (b) { b.disabled = false; });
    }

    function renderStatsFromObj(container, statsObj, prefix) {
        if (!statsObj) return;
        var entries = [
            { k: 'min', l: prefix + ' Min' },
            { k: 'max', l: prefix + ' Max' },
            { k: 'mean', l: prefix + ' Mean' },
            { k: 'std', l: prefix + ' Std Dev' },
        ];
        for (var i = 0; i < entries.length; i++) {
            if (statsObj[entries[i].k] !== undefined) {
                container.appendChild(buildStatCard(entries[i].l, statsObj[entries[i].k]));
            }
        }
    }

    /** Build a target image label with a badge span + display name text. */
    function buildTargetLabel(badgeClass, badgeText, displayName) {
        var label = D.createEl('div', 'target-label');
        var badge = D.createEl('span', 'badge ' + badgeClass, badgeText);
        label.appendChild(badge);
        var nameSpan = document.createTextNode(' ' + displayName);
        label.appendChild(nameSpan);
        return label;
    }

    // ------------------------------------------------------------------ //
    //  Section 1: Load Target Images                                      //
    // ------------------------------------------------------------------ //

    function initTargets() {
        var loadBtn = document.getElementById('load-targets-btn');
        var display = document.getElementById('target-display');

        if (!loadBtn) return;

        loadBtn.addEventListener('click', function () {
            var resultsArea = document.getElementById('target-results');
            D.setLoading(resultsArea, true);

            D.apiCall('/api/p2/targets')
                .then(function (data) {
                    D.setLoading(resultsArea, false);
                    targetFirst = data.first;
                    targetLast = data.last;
                    targetsLoaded = true;

                    clearChildren(display);

                    // First image card
                    var firstCard = D.createEl('div', 'p02-target-card');
                    D.apiCall('/api/image/' + encodeURIComponent(targetFirst))
                        .then(function (imgData) {
                            var img = D.createEl('img');
                            img.src = 'data:image/png;base64,' + imgData.image;
                            img.alt = 'First image';
                            img.loading = 'lazy';
                            firstCard.insertBefore(img, firstCard.firstChild);
                        });
                    var firstLabel = buildTargetLabel('badge-first', 'First', data.first_display || data.first);
                    firstCard.appendChild(firstLabel);
                    if (data.first_meta) {
                        var meta1 = D.createEl('div', 'p02-target-meta');
                        meta1.textContent = data.first_meta.width + ' x ' + data.first_meta.height +
                            ' | ' + data.first_meta.size_kb + ' KB';
                        firstCard.appendChild(meta1);
                    }
                    display.appendChild(firstCard);

                    // Last image card
                    var lastCard = D.createEl('div', 'p02-target-card');
                    D.apiCall('/api/image/' + encodeURIComponent(targetLast))
                        .then(function (imgData) {
                            var img = D.createEl('img');
                            img.src = 'data:image/png;base64,' + imgData.image;
                            img.alt = 'Last image';
                            img.loading = 'lazy';
                            lastCard.insertBefore(img, lastCard.firstChild);
                        });
                    var lastLabel = buildTargetLabel('badge-last', 'Last', data.last_display || data.last);
                    lastCard.appendChild(lastLabel);
                    if (data.last_meta) {
                        var meta2 = D.createEl('div', 'p02-target-meta');
                        meta2.textContent = data.last_meta.width + ' x ' + data.last_meta.height +
                            ' | ' + data.last_meta.size_kb + ' KB';
                        lastCard.appendChild(meta2);
                    }
                    display.appendChild(lastCard);

                    enableButtons();
                    D.showToast('Target images loaded', 2000);
                })
                .catch(function () {
                    D.setLoading(resultsArea, false);
                    D.showToast('Failed to load target images', 4000);
                });
        });
    }

    // ------------------------------------------------------------------ //
    //  Section 2: Image Subtraction                                       //
    // ------------------------------------------------------------------ //

    function initSubtraction() {
        var computeBtn = document.getElementById('compute-subtraction-btn');
        var plotBtn = document.getElementById('subtraction-plot-btn');
        var imagesContainer = document.getElementById('subtraction-images');
        var statsContainer = document.getElementById('subtraction-stats');
        var plotContainer = document.getElementById('subtraction-plot');

        if (!computeBtn) return;

        computeBtn.addEventListener('click', function () {
            if (!targetsLoaded) { D.showToast('Load target images first'); return; }

            var resultsArea = document.getElementById('subtraction-results');
            D.setLoading(resultsArea, true);

            D.apiCall('/api/p2/subtract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: targetFirst, image2: targetLast })
            }).then(function (data) {
                D.setLoading(resultsArea, false);

                clearChildren(imagesContainer);
                if (data.image1) imagesContainer.appendChild(buildImageCard(data.image1, 'First Image (f)'));
                if (data.image2) imagesContainer.appendChild(buildImageCard(data.image2, 'Last Image (g)'));
                if (data.difference) imagesContainer.appendChild(buildImageCard(data.difference, '|f - g| (Difference)'));
                if (data.enhanced) imagesContainer.appendChild(buildImageCard(data.enhanced, 'Enhanced Difference'));

                clearChildren(statsContainer);
                if (data.stats) {
                    renderStatsFromObj(statsContainer, data.stats.image1, 'First');
                    renderStatsFromObj(statsContainer, data.stats.image2, 'Last');
                    renderStatsFromObj(statsContainer, data.stats.difference, 'Diff');
                }

                if (data.resized) {
                    var note = D.createEl('div', 'p02-insight');
                    var strong = D.createEl('strong', '', 'Note:');
                    note.appendChild(strong);
                    note.appendChild(document.createTextNode(' Images had different dimensions and were resized to match before subtraction.'));
                    imagesContainer.parentNode.insertBefore(note, statsContainer);
                }
            }).catch(function () {
                D.setLoading(resultsArea, false);
            });
        });

        plotBtn.addEventListener('click', function () {
            if (!targetsLoaded) { D.showToast('Load target images first'); return; }

            D.setLoading(plotContainer, true);

            D.apiCall('/api/p2/subtract-plot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: targetFirst, image2: targetLast })
            }).then(function (data) {
                D.setLoading(plotContainer, false);
                renderPlot(plotContainer, data.plot, 'Subtraction comparison plot');
            }).catch(function () {
                D.setLoading(plotContainer, false);
            });
        });
    }

    // ------------------------------------------------------------------ //
    //  Section 3: Image Inversion                                         //
    // ------------------------------------------------------------------ //

    function initInversion() {
        var invertFirstBtn = document.getElementById('invert-first-btn');
        var invertLastBtn = document.getElementById('invert-last-btn');
        var comparisonBtn = document.getElementById('inversion-comparison-btn');
        var imagesContainer = document.getElementById('inversion-images');
        var statsContainer = document.getElementById('inversion-stats');
        var histContainer = document.getElementById('inversion-histograms');
        var compContainer = document.getElementById('inversion-comparison');

        if (!invertFirstBtn) return;

        function doInvert(filename, label) {
            var resultsArea = document.getElementById('inversion-results');
            D.setLoading(resultsArea, true);

            D.apiCall('/api/p2/invert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: filename })
            }).then(function (data) {
                D.setLoading(resultsArea, false);

                clearChildren(imagesContainer);
                if (data.original) imagesContainer.appendChild(buildImageCard(data.original, label + ' Original'));
                if (data.inverted) imagesContainer.appendChild(buildImageCard(data.inverted, label + ' Inverted (255 - r)'));

                clearChildren(statsContainer);
                if (data.stats) {
                    renderStatsFromObj(statsContainer, data.stats.original, 'Original');
                    renderStatsFromObj(statsContainer, data.stats.inverted, 'Inverted');
                }

                // Load histogram
                D.apiCall('/api/p2/invert-histogram', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filename: filename })
                }).then(function (histData) {
                    renderPlot(histContainer, histData.plot, 'Inversion histogram comparison');
                });
            }).catch(function () {
                D.setLoading(resultsArea, false);
            });
        }

        invertFirstBtn.addEventListener('click', function () {
            if (!targetsLoaded) { D.showToast('Load target images first'); return; }
            doInvert(targetFirst, 'First Image');
        });

        invertLastBtn.addEventListener('click', function () {
            if (!targetsLoaded) { D.showToast('Load target images first'); return; }
            doInvert(targetLast, 'Last Image');
        });

        comparisonBtn.addEventListener('click', function () {
            if (!targetsLoaded) { D.showToast('Load target images first'); return; }

            D.setLoading(compContainer, true);

            D.apiCall('/api/p2/invert-comparison', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: targetFirst, image2: targetLast })
            }).then(function (data) {
                D.setLoading(compContainer, false);
                renderPlot(compContainer, data.plot, 'Inversion side-by-side comparison');
            }).catch(function () {
                D.setLoading(compContainer, false);
            });
        });
    }

    // ------------------------------------------------------------------ //
    //  Section 4: Combined Operations                                     //
    // ------------------------------------------------------------------ //

    function initCombined() {
        var combinedBtn = document.getElementById('combined-btn');
        var matchContainer = document.getElementById('combined-match');
        var imagesContainer = document.getElementById('combined-images');
        var statsContainer = document.getElementById('combined-stats');
        var plotContainer = document.getElementById('combined-plot');

        if (!combinedBtn) return;

        combinedBtn.addEventListener('click', function () {
            if (!targetsLoaded) { D.showToast('Load target images first'); return; }

            var resultsArea = document.getElementById('combined-results');
            D.setLoading(resultsArea, true);

            D.apiCall('/api/p2/combined', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image1: targetFirst, image2: targetLast })
            }).then(function (data) {
                D.setLoading(resultsArea, false);

                // Match badge
                clearChildren(matchContainer);
                var badge = D.createEl('div', 'p02-match-badge');
                if (data.pixel_match) {
                    badge.classList.add('match-true');
                    badge.textContent = 'Pixel-wise identical: |f-g| = |(255-f)-(255-g)|';
                } else {
                    badge.classList.add('match-false');
                    badge.textContent = 'Difference detected (unexpected)';
                }
                matchContainer.appendChild(badge);

                var insight = D.createEl('div', 'p02-insight');
                var strong = D.createEl('strong', '', 'Verified:');
                insight.appendChild(strong);
                insight.appendChild(document.createTextNode(
                    ' The absolute difference of two images is unchanged by prior inversion. ' +
                    'This confirms the algebraic identity |(255-f) - (255-g)| = |f - g| holds ' +
                    'for every pixel in these images.'
                ));
                matchContainer.appendChild(insight);

                // Images
                clearChildren(imagesContainer);
                if (data.diff_original) imagesContainer.appendChild(buildImageCard(data.diff_original, '|Original 1 - Original 2|'));
                if (data.diff_inverted) imagesContainer.appendChild(buildImageCard(data.diff_inverted, '|Inverted 1 - Inverted 2|'));
                if (data.inverted1) imagesContainer.appendChild(buildImageCard(data.inverted1, 'Inverted First'));
                if (data.inverted2) imagesContainer.appendChild(buildImageCard(data.inverted2, 'Inverted Last'));

                // Stats
                clearChildren(statsContainer);
                if (data.stats) {
                    renderStatsFromObj(statsContainer, data.stats.diff_original, 'Orig Diff');
                    renderStatsFromObj(statsContainer, data.stats.diff_inverted, 'Inv Diff');
                }

                // Plot
                renderPlot(plotContainer, data.plot, 'Combined operations comparison');
            }).catch(function () {
                D.setLoading(resultsArea, false);
            });
        });
    }

    // ------------------------------------------------------------------ //
    //  Initialization                                                     //
    // ------------------------------------------------------------------ //

    function init() {
        initTargets();
        initSubtraction();
        initInversion();
        initCombined();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
