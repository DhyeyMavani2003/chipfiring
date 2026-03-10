/**
 * Chip-firing interactive behaviour for the Dash Cytoscape divisor visualizer.
 *
 *  - Chip indicator nodes follow their parent vertex when dragged.
 *  - Double-clicking a vertex fires it (single-vertex fire).
 *  - Selecting vertices + Enter / "Fire Selected" fires the set.
 *  - Selecting one vertex + B / "Burn (Dhar's)" runs Dhar's burning algorithm
 *    and animates it step by step.
 *
 * All tuneable constants are at the top of the file.
 */
(function () {
    'use strict';

    // ── Tuneable parameters ────────────────────────────────────────────────
    var ANIMATION_DURATION_MS = 500;   // chip travel time along edges (firing)
    var DOUBLE_TAP_MS         = 300;   // max gap between taps for double-tap
    var VERTEX_RADIUS         = 25;    // must match CFVisualizer.py VERTEX_RADIUS
    var DHAR_STEP_DELAY_MS    = 700;   // pause between successive burn events
    var BURN_OVERLAY_COLOR    = '#cc0000';   // colour of burnt-vertex halo
    var BURN_Q_OVERLAY_COLOR  = '#ff8800';   // colour of q (fire-source) halo
    var BURN_OVERLAY_OPACITY  = 0.38;
    var BURN_OVERLAY_PADDING  = '10px';
    var BURN_EDGE_COLOR       = '#cc0000';
    var BURN_EDGE_WIDTH       = 4;
    // ──────────────────────────────────────────────────────────────────────

    var travelCounter = 0;
    var isFiring      = false;
    var burnAnimation = { runId: 0, timeouts: [] };

    // ── Cytoscape instance discovery ──────────────────────────────────────

    function getCy(id) {
        var el = document.getElementById(id);
        if (!el) return null;
        if (el._cyreg && el._cyreg.cy) return el._cyreg.cy;
        var key = Object.keys(el).find(function (k) {
            return k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance');
        });
        if (key) {
            var fiber = el[key];
            for (var i = 0; i < 15 && fiber; i++) {
                var sn = fiber.stateNode;
                if (sn && sn._cy && typeof sn._cy.nodes === 'function') return sn._cy;
                fiber = fiber.return;
            }
        }
        return null;
    }

    // ── Chip placement (mirrors _chip_indicator_elements in CFVisualizer.py) ──

    function chipLayout(cx, cy_coord, nChips) {
        var chipR = VERTEX_RADIUS / 5;
        while (true) {
            var orbitR = VERTEX_RADIUS + chipR;
            if (Math.floor(Math.PI / Math.asin(chipR / orbitR)) >= nChips) break;
            chipR /= 2;
            if (chipR < 0.05) break;
        }
        var orbitR = VERTEX_RADIUS + chipR;
        var positions = [];
        for (var i = 0; i < nChips; i++) {
            var angle = 2 * Math.PI * i / nChips;
            positions.push({
                x:  cx + orbitR * Math.sin(angle),
                y:  cy_coord - orbitR * Math.cos(angle),
                dx: orbitR * Math.sin(angle),
                dy: -orbitR * Math.cos(angle)
            });
        }
        return { positions: positions, chipSize: chipR * 2 };
    }

    // ── Vertex state update ────────────────────────────────────────────────

    function cancelBurnAnimation() {
        burnAnimation.runId += 1;
        burnAnimation.timeouts.forEach(function (timeoutId) { clearTimeout(timeoutId); });
        burnAnimation.timeouts = [];
    }

    function updateVertex(cy, nodeId, newChips, options) {
        if (!options || !options.preserveBurnState) {
            clearBurnVisuals(cy);
        }
        var node = cy.getElementById(nodeId);
        node.data('chips_count', newChips);
        node.data('label', nodeId + '\n' + newChips);
        node.data('divisor_sign',
            newChips < 0 ? 'negative' : (newChips === 0 ? 'zero' : 'positive'));

        cy.nodes().filter(function (n) {
            return n.data('parent_vertex') === nodeId;
        }).remove();

        if (newChips !== 0) {
            var pos      = node.position();
            var n        = Math.abs(newChips);
            var layout   = chipLayout(pos.x, pos.y, n);
            var chipType = newChips > 0 ? 'positive_chip' : 'negative_chip';

            cy.add(layout.positions.map(function (p, i) {
                return {
                    data: {
                        id:            'chip_' + nodeId + '_' + i,
                        chip_type:     chipType,
                        chip_size:     layout.chipSize,
                        parent_vertex: nodeId,
                        dx:            p.dx,
                        dy:            p.dy
                    },
                    position:    { x: p.x, y: p.y },
                    selectable:  false,
                    grabbable:   false
                };
            }));
        }
    }

    // ── Core firing logic ─────────────────────────────────────────────────

    function fireVertices(cy, nodeIds) {
        if (isFiring || !nodeIds || nodeIds.length === 0) return;
        isFiring = true;
        clearBurnVisuals(cy);   // stale burn state is invalid after chip change

        var inSet = {};
        nodeIds.forEach(function (id) { inSet[id] = true; });

        var deltas     = {};
        var animations = [];

        nodeIds.forEach(function (vid) {
            if (deltas[vid] === undefined) deltas[vid] = 0;
            cy.edges().forEach(function (edge) {
                var src = edge.data('source');
                var tgt = edge.data('target');
                var neighbor = null;
                if      (src === vid) neighbor = tgt;
                else if (tgt === vid) neighbor = src;
                if (neighbor === null) return;
                deltas[vid] = deltas[vid] - 1;
                deltas[neighbor] = (deltas[neighbor] || 0) + 1;
                animations.push({ from: vid, to: neighbor });
            });
        });

        var posSnap   = {};
        var chipsSnap = {};
        Object.keys(deltas).forEach(function (id) {
            var node = cy.getElementById(id);
            var p    = node.position();
            posSnap[id]   = { x: p.x, y: p.y };
            chipsSnap[id] = node.data('chips_count') || 0;
        });

        nodeIds.forEach(function (vid) {
            if (deltas[vid] !== undefined) {
                updateVertex(cy, vid, chipsSnap[vid] + deltas[vid], { preserveBurnState: true });
            }
        });

        if (animations.length === 0) {
            Object.keys(deltas).forEach(function (id) {
                if (!inSet[id]) updateVertex(cy, id, chipsSnap[id] + deltas[id], { preserveBurnState: true });
            });
            isFiring = false;
            return;
        }

        var done  = 0;
        var total = animations.length;

        function onChipArrived() {
            if (++done < total) return;
            Object.keys(deltas).forEach(function (id) {
                if (!inSet[id]) updateVertex(cy, id, chipsSnap[id] + deltas[id], { preserveBurnState: true });
            });
            isFiring = false;
        }

        animations.forEach(function (anim) {
            var srcPos = posSnap[anim.from];
            var tgtPos = posSnap[anim.to] || (function () {
                var p = cy.getElementById(anim.to).position();
                return { x: p.x, y: p.y };
            }());

            var tid = 'traveling_' + (travelCounter++);
            cy.add({
                data: { id: tid, chip_type: 'traveling_chip', chip_size: (VERTEX_RADIUS / 5) * 2 },
                position:   { x: srcPos.x, y: srcPos.y },
                selectable: false,
                grabbable:  false
            });

            cy.getElementById(tid).animate(
                { position: { x: tgtPos.x, y: tgtPos.y } },
                {
                    duration: ANIMATION_DURATION_MS,
                    complete: function () {
                        cy.getElementById(tid).remove();
                        onChipArrived();
                    }
                }
            );
        });
    }

    // ── Dhar's burning algorithm ──────────────────────────────────────────

    /**
     * Compute the sequence of burn events for Dhar's algorithm starting from qId.
     * Uses the current chip counts stored in each node's `chips_count` data field.
     *
     * Note: this is the pure burning process; send_debt_to_q is not applied here,
     * so results are most meaningful when all non-q vertices have non-negative chips.
     *
     * Returns { q, steps: [{vertex, burn_edges:[edgeId,…]},…], result, unburnt:[…] }
     */
    function computeDharSteps(cy, qId) {
        // Snapshot chip counts from live cy data
        var chips = {};
        cy.nodes().filter(function (n) { return !n.data('chip_type'); }).forEach(function (n) {
            chips[n.id()] = n.data('chips_count') || 0;
        });

        var steps   = [{ vertex: qId, burn_edges: [] }];
        var burnt   = {};  burnt[qId] = true;
        var unburnt = {};
        cy.nodes().filter(function (n) {
            return !n.data('chip_type') && n.id() !== qId;
        }).forEach(function (n) { unburnt[n.id()] = true; });

        var changed = true;
        while (changed) {
            changed = false;
            var candidates = Object.keys(unburnt).sort();
            for (var i = 0; i < candidates.length; i++) {
                var vId = candidates[i];
                if (!unburnt[vId]) continue;

                // Find edges from vId to already-burnt vertices
                var edgesToBurnt = 0;
                var burnEdgeIds  = [];
                cy.edges().forEach(function (edge) {
                    var src = edge.data('source');
                    var tgt = edge.data('target');
                    var neighbor = null;
                    if      (src === vId) neighbor = tgt;
                    else if (tgt === vId) neighbor = src;
                    if (neighbor && burnt[neighbor]) {
                        edgesToBurnt++;
                        burnEdgeIds.push(edge.id());
                    }
                });

                if (chips[vId] < edgesToBurnt) {
                    steps.push({ vertex: vId, burn_edges: burnEdgeIds });
                    burnt[vId] = true;
                    delete unburnt[vId];
                    changed = true;
                }
            }
        }

        var unburntNames = Object.keys(unburnt).sort();
        return {
            q:       qId,
            steps:   steps,
            result:  unburntNames.length === 0 ? 'all_burned' : 'partial',
            unburnt: unburntNames
        };
    }

    // ── Burn visuals ──────────────────────────────────────────────────────

    function clearBurnVisuals(cy) {
        cancelBurnAnimation();
        cy.nodes().filter(function (n) { return !n.data('chip_type'); })
          .removeStyle('overlay-color overlay-opacity overlay-padding');
        cy.edges().removeStyle('line-color width');
        var el = document.getElementById('burn-result');
        if (el) { el.textContent = ''; el.style.color = ''; }
    }

    function burnVertex(cy, stepData, isQ) {
        var node = cy.getElementById(stepData.vertex);
        node.style({
            'overlay-color':   isQ ? BURN_Q_OVERLAY_COLOR : BURN_OVERLAY_COLOR,
            'overlay-opacity': BURN_OVERLAY_OPACITY,
            'overlay-padding': BURN_OVERLAY_PADDING
        });
        stepData.burn_edges.forEach(function (eid) {
            cy.getElementById(eid).style({
                'line-color': BURN_EDGE_COLOR,
                'width':      BURN_EDGE_WIDTH
            });
        });
    }

    function playDharAnimation(cy, data) {
        if (!data || data.error) {
            var el = document.getElementById('burn-result');
            if (el) {
                el.textContent = data ? data.error : 'Unknown error.';
                el.style.color = '#dc3545';
            }
            return;
        }

        clearBurnVisuals(cy);
        cy.nodes().unselect();

        var runId = burnAnimation.runId;
        var steps = data.steps;

        steps.forEach(function (step, i) {
            var timeoutId = setTimeout(function () {
                if (runId !== burnAnimation.runId) return;
                burnVertex(cy, step, i === 0 /* isQ */);

                // After the last step, show result
                if (i === steps.length - 1) {
                    var resultTimeoutId = setTimeout(function () {
                        if (runId !== burnAnimation.runId) return;
                        var resultEl = document.getElementById('burn-result');
                        if (resultEl) {
                            if (data.result === 'all_burned') {
                                // q-reduced requires all non-q vertices to also be non-negative
                                var hasDebt = cy.nodes().filter(function (n) {
                                    return !n.data('chip_type') && n.id() !== data.q &&
                                           (n.data('chips_count') || 0) < 0;
                                }).length > 0;
                                if (hasDebt) {
                                    resultEl.textContent =
                                        'Whole graph burned \u2014 but there is debt away from q ' +
                                        '(not q-reduced).';
                                    resultEl.style.color = '#e07000';
                                } else {
                                    resultEl.textContent =
                                        '\u2713 Whole graph burned \u2014 divisor is q-reduced.';
                                    resultEl.style.color = '#28a745';
                                }
                            } else {
                                resultEl.textContent =
                                    'Unburnt: ' + data.unburnt.join(', ') +
                                    ' \u2014 maximal legal firing set.';
                                resultEl.style.color = '#dc3545';
                                // Select unburnt vertices
                                cy.nodes().filter(function (n) {
                                    return !n.data('chip_type') &&
                                           data.unburnt.indexOf(n.id()) !== -1;
                                }).select();
                            }
                        }
                    }, DHAR_STEP_DELAY_MS / 2);
                    burnAnimation.timeouts.push(resultTimeoutId);
                }
            }, i * DHAR_STEP_DELAY_MS);
            burnAnimation.timeouts.push(timeoutId);
        });
    }

    // ── Vertex context menu (right-click) ────────────────────────────────

    function buildContextMenu(cy) {
        /** Create the context-menu DOM once; return a {show, hide, el} controller. */
        var target = null;

        // Container
        var el = document.createElement('div');
        el.style.cssText = [
            'position:fixed', 'background:#fff', 'border:1px solid #bbb',
            'border-radius:6px', 'padding:10px 12px', 'box-shadow:2px 4px 12px rgba(0,0,0,0.18)',
            'z-index:9999', 'display:none', 'min-width:170px', 'font-size:13px',
            'font-family:sans-serif'
        ].join(';');

        // Title row
        var titleEl = document.createElement('div');
        titleEl.style.cssText =
            'font-weight:bold;margin-bottom:8px;padding-bottom:5px;' +
            'border-bottom:1px solid #eee;color:#333;';
        el.appendChild(titleEl);

        // Helper: styled full-width button
        function makeBtn(label, onClick) {
            var btn = document.createElement('button');
            btn.textContent = label;
            btn.style.cssText = [
                'display:block', 'width:100%', 'padding:5px 8px', 'margin-bottom:5px',
                'cursor:pointer', 'text-align:left', 'border:1px solid #ccc',
                'border-radius:3px', 'background:#f7f7f7', 'font-size:13px'
            ].join(';');
            btn.addEventListener('mouseenter', function () { btn.style.background = '#e8e8e8'; });
            btn.addEventListener('mouseleave', function () { btn.style.background = '#f7f7f7'; });
            btn.addEventListener('click', onClick);
            return btn;
        }

        el.appendChild(makeBtn('+ Add chip', function () {
            if (target) {
                updateVertex(cy, target.id(), (target.data('chips_count') || 0) + 1);
                titleEl.textContent = 'Vertex \u201c' + target.id() + '\u201d';
                setInput.value = target.data('chips_count') || 0;
            }
        }));

        el.appendChild(makeBtn('\u2212 Remove chip', function () {
            if (target) {
                updateVertex(cy, target.id(), (target.data('chips_count') || 0) - 1);
                titleEl.textContent = 'Vertex \u201c' + target.id() + '\u201d';
                setInput.value = target.data('chips_count') || 0;
            }
        }));

        // "Set chips" row
        var setRow = document.createElement('div');
        setRow.style.cssText = 'display:flex;align-items:center;gap:6px;margin-top:4px;';

        var setLabel = document.createElement('span');
        setLabel.textContent = 'Set:';
        setLabel.style.color = '#555';

        var setInput = document.createElement('input');
        setInput.type = 'number';
        setInput.style.cssText =
            'width:58px;padding:4px 5px;border:1px solid #ccc;border-radius:3px;font-size:13px;';

        var setBtn = document.createElement('button');
        setBtn.textContent = 'OK';
        setBtn.style.cssText =
            'padding:4px 10px;cursor:pointer;border:1px solid #ccc;' +
            'border-radius:3px;background:#f7f7f7;font-size:13px;';

        function applySet() {
            var val = parseInt(setInput.value, 10);
            if (!isNaN(val) && target) {
                updateVertex(cy, target.id(), val);
                ctrl.hide();
            }
        }
        setBtn.addEventListener('click', applySet);
        setInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter')  { e.stopPropagation(); applySet(); }
            if (e.key === 'Escape') { e.stopPropagation(); ctrl.hide(); }
            // prevent Enter/B shortcuts while typing
            e.stopPropagation();
        });

        setRow.appendChild(setLabel);
        setRow.appendChild(setInput);
        setRow.appendChild(setBtn);
        el.appendChild(setRow);

        document.body.appendChild(el);

        var ctrl = {
            el: el,
            show: function (x, y, node) {
                target = node;
                titleEl.textContent = 'Vertex \u201c' + node.id() + '\u201d';
                setInput.value = node.data('chips_count') || 0;

                // Keep menu on-screen
                el.style.display = 'block';
                var mw = el.offsetWidth, mh = el.offsetHeight;
                var vw = window.innerWidth,  vh = window.innerHeight;
                el.style.left = (x + mw > vw ? vw - mw - 8 : x) + 'px';
                el.style.top  = (y + mh > vh ? vh - mh - 8 : y) + 'px';

                setTimeout(function () { setInput.select(); }, 30);
            },
            hide: function () {
                el.style.display = 'none';
                target = null;
            }
        };
        return ctrl;
    }

    // ── Event handlers ────────────────────────────────────────────────────

    function getSelectedVertexIds(cy) {
        return cy.nodes(':selected')
            .filter(function (n) { return !n.data('chip_type'); })
            .map(function (n) { return n.id(); });
    }

    var _chipHandlersAttached = false;

    function attachChipHandlers(cy) {
        // Guard: only wire up once (safe to call again after graph→divisor switch
        // because a new cy instance is not created, but new elements are loaded).
        if (_chipHandlersAttached) return;
        _chipHandlersAttached = true;

        // ── Double-tap: fire single vertex ────────────────────────────────
        var lastTap = { time: 0, nodeId: null };
        cy.on('tap', 'node', function (evt) {
            var node   = evt.target;
            if (node.data('chip_type')) return;
            var now    = Date.now();
            var nodeId = node.id();
            if (now - lastTap.time < DOUBLE_TAP_MS && lastTap.nodeId === nodeId) {
                lastTap = { time: 0, nodeId: null };
                fireVertices(cy, [nodeId]);
            } else {
                lastTap = { time: now, nodeId: nodeId };
            }
        });

        // ── "Fire Selected" button ────────────────────────────────────────
        var fireBtn = document.getElementById('fire-selected-btn');
        if (fireBtn) {
            fireBtn.addEventListener('click', function () {
                fireVertices(cy, getSelectedVertexIds(cy));
            });
        }

        // ── "Burn (Dhar's)" button ────────────────────────────────────────
        var burnBtn = document.getElementById('burn-btn');
        if (burnBtn) {
            burnBtn.addEventListener('click', function () { runBurn(cy); });
        }

        // ── "Clear Burn" button ───────────────────────────────────────────
        var clearBurnBtn = document.getElementById('clear-burn-btn');
        if (clearBurnBtn) {
            clearBurnBtn.addEventListener('click', function () { clearBurnVisuals(cy); });
        }

        // ── Keyboard shortcuts ────────────────────────────────────────────
        document.addEventListener('keydown', function (e) {
            var tag = document.activeElement && document.activeElement.tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'BUTTON') return;

            if (e.key === 'Enter') {
                fireVertices(cy, getSelectedVertexIds(cy));
            } else if (e.key === 'b' || e.key === 'B') {
                runBurn(cy);
            }
        });

        // ── Right-click context menu ──────────────────────────────────────
        var ctxMenu = buildContextMenu(cy);

        cy.on('cxttap', 'node', function (evt) {
            if (evt.target.data('chip_type')) return;  // ignore chip dots
            var orig = evt.originalEvent;
            ctxMenu.show(orig.clientX, orig.clientY, evt.target);
        });

        // Close on any click outside the menu
        document.addEventListener('mousedown', function (e) {
            if (ctxMenu.el.style.display !== 'none' && !ctxMenu.el.contains(e.target)) {
                ctxMenu.hide();
            }
        });

        // Suppress the browser's native context menu over the graph
        document.getElementById('cytoscape-graph').addEventListener('contextmenu', function (e) {
            e.preventDefault();
        });

        // ── Pan / Select mode toggle ──────────────────────────────────────
        var panBtn    = document.getElementById('mode-pan-btn');
        var selectBtn = document.getElementById('mode-select-btn');
        var ACTIVE    = { background: '#333', color: '#fff', fontWeight: 'bold'   };
        var INACTIVE  = { background: '#f0f0f0', color: '#333', fontWeight: 'normal' };

        function applyStyle(el, styles) {
            Object.keys(styles).forEach(function (k) { el.style[k] = styles[k]; });
        }
        function setMode(selectMode) {
            cy.userPanningEnabled(!selectMode);
            cy.boxSelectionEnabled(selectMode);
            if (panBtn && selectBtn) {
                applyStyle(panBtn,    selectMode ? INACTIVE : ACTIVE);
                applyStyle(selectBtn, selectMode ? ACTIVE   : INACTIVE);
            }
        }
        if (panBtn)    panBtn.addEventListener('click',    function () { setMode(false); });
        if (selectBtn) selectBtn.addEventListener('click', function () { setMode(true);  });
        setMode(false);
    }

    // ── Burn entry point ──────────────────────────────────────────────────

    function runBurn(cy) {
        var ids = getSelectedVertexIds(cy);
        var resultEl = document.getElementById('burn-result');

        if (ids.length !== 1) {
            if (resultEl) {
                resultEl.textContent = ids.length === 0
                    ? 'Select exactly one vertex as q, then press B or click Burn.'
                    : 'Select exactly one vertex as q (' + ids.length + ' selected).';
                resultEl.style.color = '#dc3545';
            }
            return;
        }
        playDharAnimation(cy, computeDharSteps(cy, ids[0]));
    }

    // ── Bootstrap ─────────────────────────────────────────────────────────

    function isDivisorMode() {
        var el = document.getElementById('viz-mode');
        return !el || el.textContent.trim() === 'divisor';
    }

    var tries = 0;
    var interval = setInterval(function () {
        if (++tries > 150) { clearInterval(interval); return; }
        var cy = getCy('cytoscape-graph');
        if (cy) {
            clearInterval(interval);

            // Always attach the drag handler (harmless in graph mode).
            // Only attach chip-specific handlers in divisor mode.
            cy.on('drag', 'node', function (evt) {
                var node = evt.target;
                if (node.data('chip_type')) return;
                var pos = node.position();
                var id  = node.id();
                cy.nodes().filter(function (n) {
                    return n.data('parent_vertex') === id;
                }).forEach(function (chip) {
                    chip.position({ x: pos.x + chip.data('dx'), y: pos.y + chip.data('dy') });
                });
            });

            if (isDivisorMode()) {
                attachChipHandlers(cy);
            }

            // Expose reinit hook for the Dash clientside callback (graph→divisor switch)
            window._reinitChipHandlers = function () {
                attachChipHandlers(cy);
            };
        }
    }, 100);

}());
