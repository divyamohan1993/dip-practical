/**
 * DIP Practical - Pixel Grid Visualization
 * Canvas-based 10x10 interactive pixel grid with hover/click.
 */
(function () {
    'use strict';

    var DIP = window.DIP || {};
    var createEl = DIP.createEl || function (tag, cls, txt) {
        var el = document.createElement(tag);
        if (cls) el.className = cls;
        if (txt !== undefined && txt !== null) el.textContent = txt;
        return el;
    };
    var clamp255 = DIP.clamp255 || function (v) { return Math.max(0, Math.min(255, Math.round(v))); };
    var apiCall = DIP.apiCall || function () { return Promise.reject(new Error('DIP.apiCall not available')); };
    var showToast = DIP.showToast || function () {};

    var pixelGridData = null;
    var pixelGridCenter = { x: 0, y: 0 };
    var pixelGridFilename = null;

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
        canvas.style.border = '1px solid var(--dip-border, #e2e8f0)';
        canvas.style.borderRadius = '6px';
        canvas.className = 'pixel-grid-canvas';

        var ctx = canvas.getContext('2d');

        function drawGrid() {
            for (var r = 0; r < rows; r++) {
                for (var c = 0; c < cols; c++) {
                    var val = clamp255(grid[r][c]);
                    ctx.fillStyle = 'rgb(' + val + ',' + val + ',' + val + ')';
                    ctx.fillRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                    ctx.strokeStyle = 'rgba(128, 128, 128, 0.3)';
                    ctx.lineWidth = 0.5;
                    ctx.strokeRect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE);
                    ctx.fillStyle = val > 128 ? '#1a1a1a' : '#f0f0f0';
                    ctx.font = '11px monospace';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(String(val), c * CELL_SIZE + CELL_SIZE / 2, r * CELL_SIZE + CELL_SIZE / 2);
                }
            }
        }
        drawGrid();

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
                if (lastHighlight.r >= 0) { drawGrid(); lastHighlight = { r: -1, c: -1 }; }
                return;
            }

            var val = clamp255(grid[row][col]);
            var actualRow = pixelGridCenter.y + row;
            var actualCol = pixelGridCenter.x + col;
            tooltip.textContent = '(' + actualCol + ', ' + actualRow + ') = ' + val + '  |  binary: ' + ('00000000' + val.toString(2)).slice(-8);
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX - canvasWrapper.getBoundingClientRect().left + 12) + 'px';
            tooltip.style.top = (e.clientY - canvasWrapper.getBoundingClientRect().top - 30) + 'px';

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
            if (lastHighlight.r >= 0) { drawGrid(); lastHighlight = { r: -1, c: -1 }; }
        });

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
                    pixelGridData = data.pixel_grid.slice(0, 10).map(function (row) { return row.slice(0, 10); });
                    renderPixelGridCanvas(container, pixelGridData);
                    showToast('Pixel grid re-centered at (' + newX + ', ' + newY + ')');
                }
            }).catch(function () {
                showToast('Failed to load pixel data at that position');
            });
        });

        var infoDiv = createEl('div', 'pixel-grid-info');
        infoDiv.style.marginTop = '8px';
        infoDiv.style.fontSize = '0.8rem';
        infoDiv.style.color = 'var(--dip-text-muted, #666)';
        infoDiv.textContent = 'Showing region from (' + pixelGridCenter.x + ', ' + pixelGridCenter.y + ') -- Image: ' + (pixelGridFilename || 'default gradient');
        container.appendChild(infoDiv);
    }

    function initPixelGrid() {
        var container = document.getElementById('pixel-grid-canvas-container') || document.getElementById('pixel-grid-container');
        if (!container) return;
        pixelGridData = generateDefaultGrid();
        renderPixelGridCanvas(container, pixelGridData);
    }

    // Expose for p01.js to call after images load
    window.DIP = window.DIP || {};
    window.DIP.pixelGrid = {
        init: initPixelGrid,
        setFilename: function (fn) { pixelGridFilename = fn; },
        setCenter: function (x, y) { pixelGridCenter = { x: x, y: y }; },
        loadFromImage: function () {
            if (!pixelGridFilename) return;
            apiCall('/api/pixel-view', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: pixelGridFilename, x: 0, y: 0, size: 10 })
            }).then(function (data) {
                if (data && data.pixel_grid) {
                    pixelGridData = data.pixel_grid.slice(0, 10).map(function (row) { return row.slice(0, 10); });
                    var container = document.getElementById('pixel-grid-canvas-container') || document.getElementById('pixel-grid-container');
                    if (container) renderPixelGridCanvas(container, pixelGridData);
                }
            }).catch(function () { /* keep default grid */ });
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPixelGrid);
    } else {
        initPixelGrid();
    }
})();
