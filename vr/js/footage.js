/**
 * Raid Footage room — sets up video panels and manages playback
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');

  // Only one video plays at a time
  scene.addEventListener('video-playing', (evt) => {
    const panels = document.querySelectorAll('#room-footage [video-panel]');
    panels.forEach(p => {
      if (p !== evt.detail.panel && p.components['video-panel']) {
        p.components['video-panel'].pause();
      }
    });
  });

  let footageLoaded = false;
  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'footage' || footageLoaded) return;
    footageLoaded = true;

    const api = window.dataAPI;
    if (!api) return;

    const contradictions = await api.getContradictions();
    if (contradictions && contradictions.data && contradictions.data.length > 0) {
      window._footageContradictions = contradictions.data;
    }

    console.log('[footage] Room data loaded');
  });
});
