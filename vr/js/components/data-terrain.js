/**
 * data-terrain — Generates a grid of data-bars from API data
 * Fetches time series data and creates a walkable terrain of bars.
 * Brutalist design: heavy concrete geometry, bold labels, cost-of-enforcement palette.
 * Usage: <a-entity data-terrain></a-entity>
 */
AFRAME.registerComponent('data-terrain', {
  schema: {
    maxHeight: { type: 'number', default: 5 },
    spacing: { type: 'number', default: 1.0 },
    barWidth: { type: 'number', default: 0.6 }
  },

  init: function () {
    this.loaded = false;
  },

  loadData: async function () {
    if (this.loaded) return;
    this.loaded = true;

    const api = window.dataAPI;
    if (!api) {
      console.error('[data-terrain] No dataAPI found');
      return;
    }

    // Corrected column names matching actual database schema
    // Cost-of-enforcement color scheme
    const metrics = [
      { table: 'detention_population', col: 'population', color: '#2C3E50', label: 'DETENTION POP.' },
      { table: 'deportations', col: 'removals', color: '#E74C3C', label: 'DEPORTATIONS' },
      { table: 'arrests', col: 'arrests', color: '#D4AC0D', label: 'ARRESTS' },
      { table: 'deaths_in_custody', col: 'deaths', color: '#C0392B', label: 'DEATHS' },
      { table: 'agency_budgets', col: 'budget_millions', color: '#D4AC0D', label: 'ICE BUDGET ($M)', filters: { agency: 'ICE' } }
    ];

    // Fetch all time series (with optional filters)
    const allData = await Promise.all(
      metrics.map(m => api.getTimeSeries(m.table, m.col, m.filters))
    );

    // Find global max per metric for normalization
    const maxVals = allData.map(series =>
      Math.max(...series.map(d => d.value || 0), 1)
    );

    // Brutalist title slab
    const titleSlab = document.createElement('a-entity');
    titleSlab.setAttribute('position', '0 4.5 -5');

    const titleBg = document.createElement('a-plane');
    titleBg.setAttribute('width', '12');
    titleBg.setAttribute('height', '1.5');
    titleBg.setAttribute('color', '#1a1a1a');
    titleSlab.appendChild(titleBg);

    const titleText = document.createElement('a-text');
    titleText.setAttribute('value', 'DATA LANDSCAPE');
    titleText.setAttribute('position', '0 0.15 0.01');
    titleText.setAttribute('align', 'center');
    titleText.setAttribute('color', '#ECF0F1');
    titleText.setAttribute('width', '8');
    titleText.setAttribute('font', 'monoid');
    titleSlab.appendChild(titleText);

    const subtitleText = document.createElement('a-text');
    subtitleText.setAttribute('value', '30 YEARS OF ENFORCEMENT DATA');
    subtitleText.setAttribute('position', '0 -0.35 0.01');
    subtitleText.setAttribute('align', 'center');
    subtitleText.setAttribute('color', '#95A5A6');
    subtitleText.setAttribute('width', '4');
    subtitleText.setAttribute('font', 'monoid');
    titleSlab.appendChild(subtitleText);

    this.el.appendChild(titleSlab);

    // Collect all years for X-axis markers
    const allYears = new Set();

    // Generate bars
    metrics.forEach((metric, zIdx) => {
      const series = allData[zIdx];
      const maxVal = maxVals[zIdx];

      series.forEach((point, xIdx) => {
        if (point.year) allYears.add(point.year);
        const normalized = (point.value / maxVal) * this.data.maxHeight;
        if (normalized <= 0) return;

        const bar = document.createElement('a-entity');
        const x = xIdx * this.data.spacing - (series.length * this.data.spacing / 2);
        const z = zIdx * (this.data.spacing * 2.5) - (metrics.length * this.data.spacing);

        bar.setAttribute('position', `${x} 0 ${z}`);
        bar.setAttribute('data-bar',
          `height: ${normalized}; color: ${metric.color}; ` +
          `width: ${this.data.barWidth}; depth: ${this.data.barWidth}; ` +
          `label: ${metric.label} ${point.year}; ` +
          `value: ${point.value ? point.value.toLocaleString() : 'N/A'}; ` +
          `source: API; trust: verified`
        );
        this.el.appendChild(bar);
      });

      // Row label — brutalist style: concrete slab with white text
      const labelGroup = document.createElement('a-entity');
      const labelZ = zIdx * (this.data.spacing * 2.5) - (metrics.length * this.data.spacing);
      const labelX = -(series.length * this.data.spacing / 2) - 2.5;
      labelGroup.setAttribute('position', `${labelX} 0.6 ${labelZ}`);

      const labelBg = document.createElement('a-plane');
      labelBg.setAttribute('width', '3');
      labelBg.setAttribute('height', '0.6');
      labelBg.setAttribute('color', '#333333');
      labelGroup.appendChild(labelBg);

      const accentBar = document.createElement('a-plane');
      accentBar.setAttribute('width', '0.08');
      accentBar.setAttribute('height', '0.6');
      accentBar.setAttribute('position', '-1.46 0 0.01');
      accentBar.setAttribute('color', metric.color);
      labelGroup.appendChild(accentBar);

      const rowLabel = document.createElement('a-text');
      rowLabel.setAttribute('value', metric.label);
      rowLabel.setAttribute('position', '0 0 0.01');
      rowLabel.setAttribute('color', '#ECF0F1');
      rowLabel.setAttribute('width', '2.5');
      rowLabel.setAttribute('font', 'monoid');
      rowLabel.setAttribute('align', 'center');
      labelGroup.appendChild(rowLabel);

      this.el.appendChild(labelGroup);
    });

    // Year markers along X-axis (below first metric row)
    const sortedYears = Array.from(allYears).sort();
    const firstSeries = allData[0];
    if (firstSeries && firstSeries.length > 0) {
      const baseZ = -(metrics.length * this.data.spacing) - 2;
      firstSeries.forEach((point, xIdx) => {
        if (!point.year) return;
        // Show every other year to avoid crowding
        if (xIdx % 2 !== 0 && firstSeries.length > 15) return;

        const x = xIdx * this.data.spacing - (firstSeries.length * this.data.spacing / 2);
        const yearLabel = document.createElement('a-text');
        yearLabel.setAttribute('value', String(point.year));
        yearLabel.setAttribute('position', `${x} 0.05 ${baseZ}`);
        yearLabel.setAttribute('rotation', '-90 0 0');
        yearLabel.setAttribute('color', '#95A5A6');
        yearLabel.setAttribute('width', '1.5');
        yearLabel.setAttribute('font', 'monoid');
        yearLabel.setAttribute('align', 'center');
        this.el.appendChild(yearLabel);
      });
    }

    console.log('[data-terrain] Terrain generated with', allData.map(d => d.length), 'series');
  }
});
