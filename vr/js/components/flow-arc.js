/**
 * flow-arc — Animated particle arc between two lat/lon points
 */
AFRAME.registerComponent('flow-arc', {
  schema: {
    fromLat: { type: 'number', default: 0 },
    fromLon: { type: 'number', default: 0 },
    toLat: { type: 'number', default: 0 },
    toLon: { type: 'number', default: 0 },
    volume: { type: 'number', default: 100 },
    color: { type: 'color', default: '#E74C3C' },
    radius: { type: 'number', default: 4 }
  },

  init: function () {
    const d = this.data;
    const THREE = AFRAME.THREE;

    const from = this._latLonToVec3(d.fromLat, d.fromLon, d.radius);
    const to = this._latLonToVec3(d.toLat, d.toLon, d.radius);

    const mid = new THREE.Vector3().addVectors(from, to).multiplyScalar(0.5);
    const liftHeight = from.distanceTo(to) * 0.3;
    mid.normalize().multiplyScalar(d.radius + liftHeight);

    const curve = new THREE.QuadraticBezierCurve3(from, mid, to);
    const points = curve.getPoints(32);

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const opacity = Math.min(0.8, 0.2 + (d.volume / 5000));
    const material = new THREE.LineBasicMaterial({
      color: new THREE.Color(d.color),
      opacity: opacity,
      transparent: true
    });

    const line = new THREE.Line(geometry, material);
    this.el.setObject3D('arc', line);
  },

  _latLonToVec3: function (lat, lon, radius) {
    const THREE = AFRAME.THREE;
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    return new THREE.Vector3(
      -(radius * Math.sin(phi) * Math.cos(theta)),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  }
});
