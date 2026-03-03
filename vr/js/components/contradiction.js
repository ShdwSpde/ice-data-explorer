/**
 * contradiction — Split display showing two conflicting data values
 */
AFRAME.registerComponent('contradiction', {
  schema: {
    metric: { type: 'string', default: '' },
    govtValue: { type: 'string', default: '' },
    govtSource: { type: 'string', default: '' },
    indepValue: { type: 'string', default: '' },
    indepSource: { type: 'string', default: '' },
    severity: { type: 'string', default: 'medium' }
  },

  init: function () {
    const d = this.data;
    const sevColors = { high: '#E74C3C', medium: '#E67E22', low: '#F1C40F' };
    const color = sevColors[d.severity] || sevColors.medium;

    const bg = document.createElement('a-plane');
    bg.setAttribute('width', '1.6');
    bg.setAttribute('height', '0.9');
    bg.setAttribute('color', '#FFFFFF');
    bg.setAttribute('opacity', '0.95');
    bg.setAttribute('position', '0 0.4 0');
    this.el.appendChild(bg);

    const border = document.createElement('a-plane');
    border.setAttribute('width', '1.62');
    border.setAttribute('height', '0.92');
    border.setAttribute('color', color);
    border.setAttribute('position', '0 0.4 -0.001');
    this.el.appendChild(border);

    const divider = document.createElement('a-plane');
    divider.setAttribute('width', '0.02');
    divider.setAttribute('height', '0.8');
    divider.setAttribute('color', color);
    divider.setAttribute('position', '0 0.4 0.01');
    divider.setAttribute('material', 'shader: flat');
    this.el.appendChild(divider);

    const title = document.createElement('a-text');
    title.setAttribute('value', `CONTESTED: ${d.metric}`);
    title.setAttribute('color', color);
    title.setAttribute('width', '2');
    title.setAttribute('align', 'center');
    title.setAttribute('position', '0 0.75 0.02');
    title.setAttribute('font', 'monoid');
    this.el.appendChild(title);

    const govtLabel = document.createElement('a-text');
    govtLabel.setAttribute('value', `GOVT: ${d.govtValue}`);
    govtLabel.setAttribute('color', '#3498DB');
    govtLabel.setAttribute('width', '1.8');
    govtLabel.setAttribute('align', 'center');
    govtLabel.setAttribute('position', '-0.4 0.45 0.02');
    govtLabel.setAttribute('font', 'monoid');
    this.el.appendChild(govtLabel);

    const govtSrc = document.createElement('a-text');
    govtSrc.setAttribute('value', d.govtSource);
    govtSrc.setAttribute('color', '#999');
    govtSrc.setAttribute('width', '1.2');
    govtSrc.setAttribute('align', 'center');
    govtSrc.setAttribute('position', '-0.4 0.25 0.02');
    govtSrc.setAttribute('font', 'monoid');
    this.el.appendChild(govtSrc);

    const indepLabel = document.createElement('a-text');
    indepLabel.setAttribute('value', `INDEP: ${d.indepValue}`);
    indepLabel.setAttribute('color', '#2ECC71');
    indepLabel.setAttribute('width', '1.8');
    indepLabel.setAttribute('align', 'center');
    indepLabel.setAttribute('position', '0.4 0.45 0.02');
    indepLabel.setAttribute('font', 'monoid');
    this.el.appendChild(indepLabel);

    const indepSrc = document.createElement('a-text');
    indepSrc.setAttribute('value', d.indepSource);
    indepSrc.setAttribute('color', '#999');
    indepSrc.setAttribute('width', '1.2');
    indepSrc.setAttribute('align', 'center');
    indepSrc.setAttribute('position', '0.4 0.25 0.02');
    indepSrc.setAttribute('font', 'monoid');
    this.el.appendChild(indepSrc);

    this.el.setAttribute('look-at', '#camera');
  }
});
