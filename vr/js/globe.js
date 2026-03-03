/**
 * Facility Globe room — loads facility data and generates markers
 */
document.addEventListener('DOMContentLoaded', () => {
  const scene = document.querySelector('a-scene');
  let globeLoaded = false;

  scene.addEventListener('room-changed', async (evt) => {
    if (evt.detail.room !== 'globe' || globeLoaded) return;
    globeLoaded = true;

    const api = window.dataAPI;
    if (!api) return;

    const container = document.querySelector('#globe-markers');
    if (!container) return;

    const facilitiesData = await api.getFacilities();
    if (!facilitiesData || !facilitiesData.data) {
      console.error('[globe] No facility data');
      return;
    }

    facilitiesData.data.forEach(f => {
      if (!f.latitude || !f.longitude) return;

      const marker = document.createElement('a-entity');
      marker.setAttribute('globe-marker',
        `lat: ${f.latitude}; lon: ${f.longitude}; ` +
        `name: ${(f.facility_name || f.name || 'Unknown').replace(/;/g, ',')}; ` +
        `capacity: ${f.capacity || 0}; ` +
        `population: ${f.current_population || f.average_population || 0}; ` +
        `operator: ${(f.operator || 'Unknown').replace(/;/g, ',')}; ` +
        `type: ${f.facility_type || 'government'}`
      );
      container.appendChild(marker);
    });

    const deportData = await api.getDeportationsByNationality();
    if (deportData && deportData.data) {
      const arcContainer = document.querySelector('#globe-arcs');
      const centroids = {
        'Mexico': { lat: 23.6, lon: -102.5 },
        'Guatemala': { lat: 15.5, lon: -90.2 },
        'Honduras': { lat: 14.1, lon: -87.2 },
        'El Salvador': { lat: 13.7, lon: -89.2 },
        'Colombia': { lat: 4.6, lon: -74.1 },
        'Ecuador': { lat: -1.8, lon: -78.2 },
        'Brazil': { lat: -14.2, lon: -51.9 },
        'Dominican Republic': { lat: 18.7, lon: -70.2 },
        'Haiti': { lat: 19.0, lon: -72.4 },
        'Jamaica': { lat: 18.1, lon: -77.3 },
        'India': { lat: 20.6, lon: 78.9 },
        'China': { lat: 35.9, lon: 104.2 }
      };

      const usLat = 38.9;
      const usLon = -77.0;

      deportData.data.forEach(d => {
        const country = d.nationality || d.country;
        const dest = centroids[country];
        if (!dest) return;

        const arc = document.createElement('a-entity');
        arc.setAttribute('flow-arc',
          `fromLat: ${usLat}; fromLon: ${usLon}; ` +
          `toLat: ${dest.lat}; toLon: ${dest.lon}; ` +
          `volume: ${d.total_deported || d.removals || 100}; ` +
          `color: #E74C3C`
        );
        arcContainer.appendChild(arc);
      });
    }

    console.log('[globe] Facility globe loaded');
  });
});
