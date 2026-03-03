/**
 * data-terrain — Generates a grid of data-bars from API data
 * Fetches time series data and creates a walkable terrain of bars.
 * Usage: <a-entity data-terrain></a-entity>
 */
AFRAME.registerComponent('data-terrain', {
  schema: {
    maxHeight: { type: 'number', default: 5 },
    spacing: { type: 'number', default: 0.8 },
    barWidth: { type: 'number', default: 0.5 }
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

    // Define metrics: table, column, color, label
    const metrics = [
      { table: 'detention_population', col: 'total_detained', color: '#3498DB', label: 'Detention' },
      { table: 'deportations', col: 'total_removals', color: '#E74C3C', label: 'Deportations' },
      { table: 'arrests', col: 'total_arrests', color: '#E67E22', label: 'Arrests' },
      { table: 'deaths_in_custody', col: 'total_deaths', color: '#2C3E50', label: 'Deaths' },
      { table: 'agency_budgets', col: 'ice_budget_millions', color: '#F1C40F', label: 'Budget ($M)' }
    ];

    // Fetch all time series
    const allData = await Promise.all(
      metrics.map(m => api.getTimeSeries(m.table, m.col))
    );

    // Find global max per metric for normalization
    const maxVals = allData.map(series =>
      Math.max(...series.map(d => d.value || 0), 1)
    );

    // Generate bars
    metrics.forEach((metric, zIdx) => {
      const series = allData[zIdx];
      const maxVal = maxVals[zIdx];

      series.forEach((point, xIdx) => {
        const normalized = (point.value / maxVal) * this.data.maxHeight;
        if (normalized <= 0) return;

        const bar = document.createElement('a-entity');
        const x = xIdx * this.data.spacing - (series.length * this.data.spacing / 2);
        const z = zIdx * (this.data.spacing * 2) - (metrics.length * this.data.spacing);

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

      // Row label
      const rowLabel = document.createElement('a-text');
      const labelZ = zIdx * (this.data.spacing * 2) - (metrics.length * this.data.spacing);
      rowLabel.setAttribute('value', metric.label);
      rowLabel.setAttribute('position', `${-(series.length * this.data.spacing / 2) - 1.5} 0.5 ${labelZ}`);
      rowLabel.setAttribute('color', metric.color);
      rowLabel.setAttribute('width', '3');
      rowLabel.setAttribute('font', 'monoid');
      rowLabel.setAttribute('align', 'right');
      this.el.appendChild(rowLabel);
    });

    console.log('[data-terrain] Terrain generated');
  }
});
