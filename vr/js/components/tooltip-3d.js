/**
 * tooltip-3d — Billboard text card that faces user, shown on hover
 * Usage: <a-entity tooltip-3d="title: Deaths 2024; value: 32; source: ICE.gov; trust: contested"></a-entity>
 */
AFRAME.registerComponent('tooltip-3d', {
  schema: {
    title: { type: 'string', default: '' },
    value: { type: 'string', default: '' },
    source: { type: 'string', default: '' },
    trust: { type: 'string', default: 'verified' },
    visible: { type: 'boolean', default: false }
  },

  init: function () {
    this.card = document.createElement('a-entity');
    this.card.setAttribute('visible', this.data.visible);

    // Background panel
    const bg = document.createElement('a-plane');
    bg.setAttribute('width', 1.2);
    bg.setAttribute('height', 0.6);
    bg.setAttribute('color', '#FFFFFF');
    bg.setAttribute('opacity', 0.95);
    bg.setAttribute('side', 'double');
    this.card.appendChild(bg);

    // Border
    const border = document.createElement('a-plane');
    border.setAttribute('width', 1.22);
    border.setAttribute('height', 0.62);
    border.setAttribute('color', this._trustColor());
    border.setAttribute('position', '0 0 -0.001');
    border.setAttribute('side', 'double');
    this.card.appendChild(border);

    // Title
    const title = document.createElement('a-text');
    title.setAttribute('value', this.data.title);
    title.setAttribute('color', '#333');
    title.setAttribute('width', 2);
    title.setAttribute('position', '-0.5 0.15 0.01');
    title.setAttribute('font', 'monoid');
    this.card.appendChild(title);

    // Value
    const value = document.createElement('a-text');
    value.setAttribute('value', this.data.value);
    value.setAttribute('color', '#000');
    value.setAttribute('width', 3);
    value.setAttribute('position', '-0.5 -0.02 0.01');
    value.setAttribute('font', 'monoid');
    this.card.appendChild(value);

    // Source + trust
    const source = document.createElement('a-text');
    source.setAttribute('value', this.data.source + ' [' + this.data.trust + ']');
    source.setAttribute('color', '#999');
    source.setAttribute('width', 1.5);
    source.setAttribute('position', '-0.5 -0.2 0.01');
    source.setAttribute('font', 'monoid');
    this.card.appendChild(source);

    // Billboard: face camera
    this.card.setAttribute('look-at', '#camera');

    this.card.setAttribute('position', '0 0.8 0');
    this.el.appendChild(this.card);
  },

  _trustColor: function () {
    const colors = {
      verified: '#2ECC71',
      contested: '#E67E22',
      govt: '#3498DB',
      neutral: '#95A5A6'
    };
    return colors[this.data.trust] || colors.neutral;
  },

  show: function () {
    this.card.setAttribute('visible', true);
  },

  hide: function () {
    this.card.setAttribute('visible', false);
  }
});
