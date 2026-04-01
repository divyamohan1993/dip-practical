/**
 * DIP Practical - Plotting (Static Edition)
 * Canvas-based image display + Chart.js wrappers for histograms and line charts.
 * Requires Chart.js loaded from CDN.
 */
(function () {
    'use strict';
    window.DIP = window.DIP || {};
    DIP.draw = {};
    DIP.chart = {};

    // ---- Draw grayscale image on canvas ----
    DIP.draw.gray = function(canvas, gray, w, h) {
        canvas.width = w;
        canvas.height = h;
        var ctx = canvas.getContext('2d');
        var id = DIP.grayToImageData(gray, w, h);
        ctx.putImageData(id, 0, 0);
    };

    // ---- Create figure layout with panels ----
    // Returns array of objects: {canvas, chartBox} for each panel
    DIP.figure = function(container, title, cols, panels) {
        container.textContent = '';

        if (title) {
            var titleEl = DIP.createEl('div', 'figure-title', title);
            container.appendChild(titleEl);
        }

        var grid = DIP.createEl('div', 'result-grid');
        grid.style.gridTemplateColumns = 'repeat(' + cols + ', 1fr)';

        var result = [];

        panels.forEach(function(panel) {
            var cell = DIP.createEl('div', 'result-panel');

            if (panel.type === 'chart') {
                var chartBox = DIP.createEl('div', 'chart-panel');
                var canvas = document.createElement('canvas');
                chartBox.appendChild(canvas);
                cell.appendChild(chartBox);
                result.push({ canvas: canvas, chartBox: chartBox });
            } else {
                var canvas = document.createElement('canvas');
                canvas.style.maxWidth = '100%';
                canvas.style.height = 'auto';
                cell.appendChild(canvas);
                result.push({ canvas: canvas });
            }

            if (panel.title) {
                cell.appendChild(DIP.createEl('div', 'panel-label', panel.title));
            }

            grid.appendChild(cell);
        });

        container.appendChild(grid);
        return result;
    };

    // ---- Chart.js theme-aware defaults ----
    function chartColors() {
        var isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        return {
            text: isDark ? '#d1d5db' : '#374151',
            grid: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
            bg: 'transparent',
        };
    }

    // ---- Histogram bar chart ----
    DIP.chart.histogram = function(canvas, histOrGray, opts) {
        opts = opts || {};
        var hist;
        if (histOrGray.length === 256 && histOrGray instanceof Uint32Array) {
            hist = histOrGray;
        } else if (histOrGray.length === 256 && histOrGray instanceof Float64Array) {
            hist = histOrGray;
        } else {
            hist = DIP.histogram(histOrGray);
        }

        var colors = chartColors();
        var labels = [];
        var data = [];
        for (var i = 0; i < 256; i++) { labels.push(i); data.push(hist[i]); }

        if (canvas._chartInstance) canvas._chartInstance.destroy();
        canvas._chartInstance = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: opts.color || 'rgba(70,130,180,0.85)',
                    borderWidth: 0,
                    barPercentage: 1,
                    categoryPercentage: 1,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { display: !!opts.title, text: opts.title || '', color: colors.text, font: { size: 13, weight: 'bold' } },
                    tooltip: { enabled: true, mode: 'index', intersect: false },
                },
                scales: {
                    x: {
                        title: { display: true, text: opts.xlabel || 'Pixel Intensity', color: colors.text },
                        ticks: { maxTicksLimit: 6, color: colors.text },
                        grid: { display: false },
                    },
                    y: {
                        title: { display: true, text: opts.ylabel || 'Frequency', color: colors.text },
                        beginAtZero: true,
                        ticks: { color: colors.text },
                        grid: { color: colors.grid },
                    }
                },
                animation: false,
            }
        });
    };

    // ---- Line chart (CDF, transformation curves, etc.) ----
    DIP.chart.line = function(canvas, datasets, opts) {
        opts = opts || {};
        var colors = chartColors();

        var maxLen = 0;
        datasets.forEach(function(ds) { if (ds.y.length > maxLen) maxLen = ds.y.length; });
        var labels = [];
        for (var i = 0; i < maxLen; i++) labels.push(i);

        var chartDatasets = datasets.map(function(ds) {
            return {
                label: ds.label || '',
                data: Array.from(ds.y),
                borderColor: ds.color || 'steelblue',
                backgroundColor: 'transparent',
                borderWidth: ds.lineWidth || 2,
                borderDash: ds.dash ? [5, 5] : [],
                pointRadius: 0,
                tension: 0,
            };
        });

        if (canvas._chartInstance) canvas._chartInstance.destroy();
        canvas._chartInstance = new Chart(canvas, {
            type: 'line',
            data: { labels: labels, datasets: chartDatasets },
            options: {
                responsive: true,
                maintainAspectRatio: opts.aspect === 'equal',
                plugins: {
                    legend: { display: datasets.length > 1, labels: { color: colors.text } },
                    title: { display: !!opts.title, text: opts.title || '', color: colors.text, font: { size: 13, weight: 'bold' } },
                    tooltip: { mode: 'index', intersect: false },
                },
                scales: {
                    x: {
                        title: { display: !!opts.xlabel, text: opts.xlabel || '', color: colors.text },
                        ticks: { maxTicksLimit: 6, color: colors.text },
                        grid: { color: opts.grid !== false ? colors.grid : 'transparent' },
                        min: opts.xlim ? opts.xlim[0] : undefined,
                        max: opts.xlim ? opts.xlim[1] : undefined,
                    },
                    y: {
                        title: { display: !!opts.ylabel, text: opts.ylabel || '', color: colors.text },
                        ticks: { color: colors.text },
                        grid: { color: opts.grid !== false ? colors.grid : 'transparent' },
                        min: opts.ylim ? opts.ylim[0] : undefined,
                        max: opts.ylim ? opts.ylim[1] : undefined,
                    }
                },
                animation: false,
            }
        });
    };
})();
