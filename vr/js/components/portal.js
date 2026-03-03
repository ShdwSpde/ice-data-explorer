/**
 * portal — Clickable gateway that triggers room transitions
 * Usage: <a-entity portal="target: landscape; label: Data Landscape; color: #4CC3D9"></a-entity>
 */
AFRAME.registerComponent('portal', {
  schema: {
    target: { type: 'string' },
    label: { type: 'string' },
    color: { type: 'color', default: '#4CC3D9' },
    width: { type: 'number', default: 1.5 },
    height: { type: 'number', default: 2.2 }
  },

  init: function () {
    const d = this.data;

    // Portal frame (rectangle outline)
    const frame = document.createElement('a-entity');
    frame.setAttribute('geometry', `primitive: box; width: ${d.width}; height: ${d.height}; depth: 0.05`);
    frame.setAttribute('material', `color: ${d.color}; opacity: 0.15; transparent: true`);
    frame.classList.add('clickable');
    this.el.appendChild(frame);

    // Inner glow plane
    const inner = document.createElement('a-entity');
    inner.setAttribute('geometry', `primitive: plane; width: ${d.width - 0.1}; height: ${d.height - 0.1}`);
    inner.setAttribute('material', `color: ${d.color}; opacity: 0.08; transparent: true; shader: flat; side: double`);
    inner.setAttribute('position', '0 0 0.03');
    this.el.appendChild(inner);

    // Border edges (4 thin boxes)
    const borderWidth = 0.03;
    const borders = [
      { pos: `0 ${d.height / 2} 0`, scale: `${d.width} ${borderWidth} ${borderWidth}` },
      { pos: `0 ${-d.height / 2} 0`, scale: `${d.width} ${borderWidth} ${borderWidth}` },
      { pos: `${-d.width / 2} 0 0`, scale: `${borderWidth} ${d.height} ${borderWidth}` },
      { pos: `${d.width / 2} 0 0`, scale: `${borderWidth} ${d.height} ${borderWidth}` },
    ];
    borders.forEach(b => {
      const edge = document.createElement('a-entity');
      edge.setAttribute('geometry', 'primitive: box; width: 1; height: 1; depth: 1');
      edge.setAttribute('scale', b.scale);
      edge.setAttribute('position', b.pos);
      edge.setAttribute('material', `color: ${d.color}; shader: flat; emissive: ${d.color}; emissiveIntensity: 0.5`);
      this.el.appendChild(edge);
    });

    // Label above portal
    const label = document.createElement('a-text');
    label.setAttribute('value', d.label);
    label.setAttribute('align', 'center');
    label.setAttribute('position', `0 ${d.height / 2 + 0.3} 0`);
    label.setAttribute('color', '#333');
    label.setAttribute('width', '3');
    label.setAttribute('font', 'monoid');
    this.el.appendChild(label);

    // Click handler
    frame.addEventListener('click', () => {
      console.log(`[portal] Clicked: ${d.target}`);
      this.el.sceneEl.emit('room-change', { room: d.target });
    });

    // Hover effect
    frame.addEventListener('mouseenter', () => {
      frame.setAttribute('material', 'opacity', 0.3);
    });
    frame.addEventListener('mouseleave', () => {
      frame.setAttribute('material', 'opacity', 0.15);
    });
  }
});
