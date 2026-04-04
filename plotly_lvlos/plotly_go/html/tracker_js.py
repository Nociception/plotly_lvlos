def build_tracker_js() -> str:
    return """
    <script>
    (function() {
        const DEFAULT_COLOR = '#636efa';
        const HIGHLIGHT_COLOR = '#00e5ff';
        const HIGHLIGHT_SIZE_FACTOR = 1.8;

        let selectedEntity = null;

        function getLeftDiv() {
            return document.querySelector('.fig-left .plotly-graph-div');
        }

        function getRightDiv() {
            return document.querySelector('.fig-right .plotly-graph-div');
        }

        function applyHighlight() {
            const gd = getLeftDiv();
            if (!gd || !gd._fullData) return;

            [0, 1].forEach(function(traceIdx) {
                const trace = gd._fullData[traceIdx];
                if (!trace || !trace.ids) return;

                const ids = trace.ids;
                const baseSizes = gd.data[traceIdx].marker.size;

                const colors = ids.map(id =>
                    id === selectedEntity ? HIGHLIGHT_COLOR : DEFAULT_COLOR
                );
                const sizes = Array.isArray(baseSizes)
                    ? baseSizes.map((s, i) =>
                        ids[i] === selectedEntity ? s * HIGHLIGHT_SIZE_FACTOR : s
                      )
                    : baseSizes;
                const lineWidths = ids.map(id =>
                    id === selectedEntity ? 3 : 0
                );
                const lineColors = ids.map(id =>
                    id === selectedEntity ? '#000000' : 'rgba(0,0,0,0)'
                );

                Plotly.restyle(gd, {
                    'marker.color': [colors],
                    'marker.size': [sizes],
                    'marker.line.width': [lineWidths],
                    'marker.line.color': [lineColors],
                }, [traceIdx]);
            });
        }

        function hookAnimationEnd() {
            const gd = getLeftDiv();
            if (!gd) return;
            gd.on('plotly_animated', () => applyHighlight());
        }

        function hookEntityMenu() {
            const gd = getRightDiv();
            if (!gd) return;
            gd.on('plotly_buttonclicked', function(data) {
                if (data.menu._index !== 1) return;
                const label = data.button.label;
                selectedEntity = (label === 'Track entity') ? null : label;
                applyHighlight();
            });
        }

        window.addEventListener('load', function() {
            setTimeout(function() {
                window.dispatchEvent(new Event('resize'));
                hookAnimationEnd();
                hookEntityMenu();
            }, 100);
        });
    })();
    </script>
    """