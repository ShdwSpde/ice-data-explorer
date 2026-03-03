/**
 * Data Landscape room initialization
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  scene.addEventListener('room-changed', (evt) => {
    if (evt.detail.room === 'landscape') {
      const terrain = document.querySelector('#room-landscape [data-terrain]');
      if (terrain) {
        terrain.components['data-terrain'].loadData();
      }
    }
  });
});
