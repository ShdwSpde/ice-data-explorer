/**
 * DataAPI — Fetch wrapper for ICE Data Explorer REST API
 * Caches responses in memory. Fetches on room entry.
 */
class DataAPI {
  constructor(baseUrl = '') {
    // Default to same origin; override for cross-origin
    this.baseUrl = baseUrl || window.location.origin.replace(':8081', ':8050');
    this.cache = new Map();
  }

  async _fetch(endpoint) {
    if (this.cache.has(endpoint)) {
      return this.cache.get(endpoint);
    }
    const url = `${this.baseUrl}${endpoint}`;
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`API ${res.status}: ${url}`);
      const json = await res.json();
      this.cache.set(endpoint, json);
      return json;
    } catch (err) {
      console.error(`[DataAPI] Failed: ${endpoint}`, err);
      return null;
    }
  }

  async getStatistics() {
    return this._fetch('/api/statistics');
  }

  async getSources() {
    return this._fetch('/api/sources');
  }

  async getContradictions() {
    return this._fetch('/api/contradictions');
  }

  async getProvenance() {
    return this._fetch('/api/provenance');
  }

  async getTable(name, limit = 1000, offset = 0) {
    return this._fetch(`/api/tables/${name}?limit=${limit}&offset=${offset}`);
  }

  async getFacilities() {
    return this.getTable('detention_facilities');
  }

  async getPolicyEvents() {
    return this.getTable('policy_events');
  }

  async getDeportationsByNationality() {
    return this.getTable('deportations_by_nationality');
  }

  /**
   * Fetch a time series table and reshape into { year: value } objects.
   * Expects the table to have a 'year' column.
   */
  async getTimeSeries(tableName, valueColumn) {
    const result = await this.getTable(tableName);
    if (!result || !result.data) return [];
    return result.data.map(row => ({
      year: row.year || row.fiscal_year,
      value: row[valueColumn] || 0,
      ...row
    }));
  }

  clearCache() {
    this.cache.clear();
  }
}

// Global singleton
window.dataAPI = new DataAPI();
