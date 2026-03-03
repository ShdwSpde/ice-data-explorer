/**
 * globe-marker — Facility pin on inverted sphere
 */
AFRAME.registerComponent('globe-marker', {
  schema: {
    lat: { type: 'number', default: 0 },
    lon: { type: 'number', default: 0 },
    name: { type: 'string', default: '' },
    capacity: { type: 'number', default: 0 },
    population: { type: 'number', default: 0 },
    operator: { type: 'string', default: '' },
    type: { type: 'string', default: 'government' },
    radius: { type: 'number', default: 4 }
  },

  init: function () {
    const d = this.data;
    const pos = this._latLonToVec3(d.lat, d.lon, d.radius);
    this.el.setAttribute('position', pos);

    const colors = { private: '#E74C3C', government: '#3498DB', mixed: '#9B59B6' };
    const color = colors[d.type] || colors.government;
    const pinHeight = Math.max(0.1, (d.capacity / 5000) * 0.5);

    const pin = document.createElement('a-cylinder');
    pin.setAttribute('radius', 0.03);
    pin.setAttribute('height', pinHeight);
    pin.setAttribute('color', color);
    pin.setAttribute('opacity', 0.9);
    pin.classList.add('clickable');
    this.el.appendChild(pin);

    const fillPct = d.capacity > 0 ? d.population / d.capacity : 0;
    const pulse = document.createElement('a-sphere');
    pulse.setAttribute('radius', 0.05 + fillPct * 0.05);
    pulse.setAttribute('color', color);
    pulse.setAttribute('opacity', 0.4 + fillPct * 0.4);
    pulse.setAttribute('position', `0 ${pinHeight / 2 + 0.05} 0`);
    this.el.appendChild(pulse);

    const tip = document.createElement('a-entity');
    tip.setAttribute('tooltip-3d',
      `title: ${d.name}; ` +
      `value: ${d.population.toLocaleString()} / ${d.capacity.toLocaleString()}; ` +
      `source: ${d.operator}; ` +
      `trust: ${d.type === 'private' ? 'contested' : 'govt'}; visible: false`
    );
    tip.setAttribute('position', `0 ${pinHeight + 0.8} 0`);
    this.el.appendChild(tip);
    this.tip = tip;

    pin.addEventListener('mouseenter', () => {
      if (this.tip.components['tooltip-3d']) this.tip.components['tooltip-3d'].show();
    });
    pin.addEventListener('mouseleave', () => {
      if (this.tip.components['tooltip-3d']) this.tip.components['tooltip-3d'].hide();
    });
  },

  _latLonToVec3: function (lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    const x = -(radius * Math.sin(phi) * Math.cos(theta));
    const y = radius * Math.cos(phi);
    const z = radius * Math.sin(phi) * Math.sin(theta);
    return `${x.toFixed(3)} ${y.toFixed(3)} ${z.toFixed(3)}`;
  }
});
