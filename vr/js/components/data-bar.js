/**
 * data-bar — A single 3D bar rising from the ground
 * Usage: <a-entity data-bar="height: 2; color: #4CC3D9; label: 2020; value: 45000"></a-entity>
 */
AFRAME.registerComponent('data-bar', {
  schema: {
    height: { type: 'number', default: 1 },
    color: { type: 'color', default: '#4CC3D9' },
    width: { type: 'number', default: 0.3 },
    depth: { type: 'number', default: 0.3 },
    label: { type: 'string', default: '' },
    value: { type: 'string', default: '' },
    source: { type: 'string', default: '' },
    trust: { type: 'string', default: 'verified' }
  },

  init: function () {
    const d = this.data;

    // Bar geometry — positioned so bottom sits at y=0
    const bar = document.createElement('a-box');
    bar.setAttribute('width', d.width);
    bar.setAttribute('height', d.height);
    bar.setAttribute('depth', d.depth);
    bar.setAttribute('position', `0 ${d.height / 2} 0`);
    bar.setAttribute('color', d.color);
    bar.setAttribute('opacity', 0.85);
    bar.classList.add('clickable');
    this.el.appendChild(bar);
    this.bar = bar;

    // Tooltip (hidden by default)
    const tip = document.createElement('a-entity');
    tip.setAttribute('tooltip-3d', `title: ${d.label}; value: ${d.value}; source: ${d.source}; trust: ${d.trust}; visible: false`);
    tip.setAttribute('position', `0 ${d.height + 0.5} 0`);
    this.el.appendChild(tip);
    this.tip = tip;

    // Hover handlers
    bar.addEventListener('mouseenter', () => {
      bar.setAttribute('opacity', 1.0);
      tip.components['tooltip-3d'].show();
    });
    bar.addEventListener('mouseleave', () => {
      bar.setAttribute('opacity', 0.85);
      tip.components['tooltip-3d'].hide();
    });
  }
});
