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
   * Fetch a time series table and reshape into { year, value, ...row } objects.
   * Expects the table to have a 'year' column.
   * @param {string} tableName - API table name
   * @param {string} valueColumn - Column to extract as 'value'
   * @param {Object} [filters] - Optional key/value pairs for client-side row filtering
   */
  async getTimeSeries(tableName, valueColumn, filters) {
    const result = await this.getTable(tableName);
    if (!result || !result.data) return [];
    let rows = result.data;
    // Client-side filtering (e.g., { agency: 'ICE' })
    if (filters) {
      rows = rows.filter(row => {
        return Object.entries(filters).every(([key, val]) => row[key] === val);
      });
    }
    return rows.map(row => ({
      year: row.year || row.fiscal_year,
      value: row[valueColumn] || 0,
      ...row
    }));
  }

  clearCache() {
    this.cache.clear();
  }
}

/**
 * Memorial data — 14 documented deaths in ICE custody
 * Source: ACLU, Human Rights Watch, ICE FOIA, news reports
 * Mirrored from pages/memorial.py for VR access
 */
DataAPI.MEMORIAL_DATA = [
  {
    name: 'Roxsana Hernández',
    age: 33,
    origin: 'Honduras',
    date: 'May 25, 2018',
    facility: 'Cibola County Correctional Center, NM',
    cause: 'Complications from HIV, dehydration',
    detained_days: 16,
    story: 'Roxsana was a transgender woman who fled persecution in Honduras. She presented herself at a port of entry seeking asylum. Despite visible signs of illness, she was held in an ice box detention cell for days before being transferred. An independent autopsy revealed signs of abuse.',
    source: 'ACLU, Transgender Law Center'
  },
  {
    name: 'Jakelin Caal Maquín',
    age: 7,
    origin: 'Guatemala',
    date: 'December 8, 2018',
    facility: 'CBP Custody, Lordsburg, NM',
    cause: 'Sepsis, dehydration',
    detained_days: 2,
    story: 'Jakelin and her father crossed the border seeking asylum. She developed a high fever while in custody but medical attention was delayed for hours. She died of septic shock at a hospital in El Paso.',
    source: 'DHS OIG Report, CBS News'
  },
  {
    name: 'Carlos Gregorio Hernandez Vasquez',
    age: 16,
    origin: 'Guatemala',
    date: 'May 20, 2019',
    facility: 'CBP Holding Facility, Weslaco, TX',
    cause: 'Influenza complications',
    detained_days: 6,
    story: 'Carlos was diagnosed with the flu and a 103-degree fever but was not hospitalized. He was found unresponsive on the floor of his cell. Video showed he had been lying motionless for hours before anyone checked on him.',
    source: 'ProPublica, DHS OIG'
  },
  {
    name: 'Huy Chi Tran',
    age: 47,
    origin: 'Vietnam',
    date: 'February 2019',
    facility: 'Prairieland Detention Center, TX',
    cause: 'Suicide',
    detained_days: 180,
    story: 'Huy was a legal permanent resident facing deportation after a criminal conviction. He had lived in the US for over 30 years. His family said he became increasingly despondent during his prolonged detention.',
    source: 'RAICES, Houston Chronicle'
  },
  {
    name: 'Johana Medina León',
    age: 25,
    origin: 'El Salvador',
    date: 'June 1, 2019',
    facility: 'Otero County Processing Center, NM',
    cause: 'HIV complications, cardiac arrest',
    detained_days: 4,
    story: 'Johana was a transgender woman with HIV who sought asylum at a port of entry. Despite disclosing her medical condition, she did not receive adequate care. She died in a hospital days after being released from ICE custody.',
    source: 'Diversidad Sin Fronteras, NBC News'
  },
  {
    name: 'Fernando Dominguez',
    age: 59,
    origin: 'Mexico',
    date: 'October 2019',
    facility: 'Stewart Detention Center, GA',
    cause: 'Heart attack, delayed care',
    detained_days: 270,
    story: 'Fernando had multiple chronic conditions including diabetes and heart disease. His family said he repeatedly complained about inadequate medical care. He suffered a fatal heart attack after months in detention.',
    source: 'Project South, Atlanta Journal-Constitution'
  },
  {
    name: 'Nebane Abienwi',
    age: 37,
    origin: 'Cameroon',
    date: 'October 2019',
    facility: 'San Diego ICE Custody',
    cause: 'Brain hemorrhage',
    detained_days: 14,
    story: 'Nebane was an asylum seeker who fled political violence in Cameroon. He collapsed in detention and was rushed to a hospital where he died. His family believes his complaints of severe headaches were ignored.',
    source: 'ACLU San Diego, Voice of San Diego'
  },
  {
    name: 'Choung Woong Ahn',
    age: 74,
    origin: 'South Korea',
    date: 'December 2019',
    facility: 'Mesa Verde ICE Processing Center, CA',
    cause: 'Complications from fall',
    detained_days: 90,
    story: 'Choung was the oldest person to die in ICE custody. He was a legal permanent resident detained for a decades-old conviction. He fell and suffered a brain bleed but was not immediately taken to a hospital.',
    source: 'San Francisco Chronicle, CIVIC'
  },
  {
    name: 'Carlos Escobar-Mejia',
    age: 57,
    origin: 'El Salvador',
    date: 'May 2020',
    facility: 'Otay Mesa Detention Center, CA',
    cause: 'COVID-19',
    detained_days: 45,
    story: 'Carlos was the first person known to die of COVID-19 in ICE custody. He had been denied release despite the pandemic and his underlying health conditions. The facility had a major outbreak.',
    source: 'LA Times, ACLU'
  },
  {
    name: 'Santiago Baten-Oxlaj',
    age: 34,
    origin: 'Guatemala',
    date: 'July 2020',
    facility: 'Stewart Detention Center, GA',
    cause: 'COVID-19 complications',
    detained_days: 60,
    story: 'Santiago died after a COVID-19 outbreak at Stewart Detention Center. He had underlying conditions that made him high-risk. Advocates had called for his release weeks before his death.',
    source: 'El Refugio, Project South'
  },
  {
    name: 'Onoval Perez-Montufa',
    age: 51,
    origin: 'Guatemala',
    date: 'August 2020',
    facility: 'Farmville Detention Center, VA',
    cause: 'COVID-19',
    detained_days: 120,
    story: 'Onoval died during a massive COVID outbreak at Farmville that infected over 300 detainees. The facility had been cited for inadequate medical care. He leaves behind children in the US.',
    source: 'ACLU Virginia, Washington Post'
  },
  {
    name: 'Cipriano Chavez-Alvarez',
    age: 61,
    origin: 'Mexico',
    date: 'September 2020',
    facility: 'Eloy Detention Center, AZ',
    cause: 'COVID-19',
    detained_days: 90,
    story: 'Cipriano died after contracting COVID-19 in detention. His family had been trying to secure his release for months. Eloy Detention Center has had one of the highest death rates of any ICE facility.',
    source: 'ACLU Arizona, Arizona Republic'
  },
  {
    name: 'Oscar Lopez Acosta',
    age: 44,
    origin: 'Mexico',
    date: 'February 2021',
    facility: 'Stewart Detention Center, GA',
    cause: 'Hypertensive cardiovascular disease',
    detained_days: 180,
    story: 'Oscar had been in detention for six months when he died of heart disease. His family said he had been complaining of chest pains for weeks but was told it was anxiety. He leaves behind three children.',
    source: 'Project South, Georgia Detention Watch'
  },
  {
    name: 'Kesley Vial',
    age: 45,
    origin: 'Haiti',
    date: 'March 2021',
    facility: 'Torrance County Detention Facility, NM',
    cause: 'Cardiac arrest, medical neglect',
    detained_days: 60,
    story: 'Kesley complained of chest pains for days before collapsing. Despite having a known heart condition, he was not given his prescribed medication. His death prompted calls for facility closure.',
    source: 'ACLU New Mexico, NPR'
  },
  {
    name: 'Abelardo Avellaneda-Delgado',
    age: 68,
    origin: 'Mexico (lived in Georgia 20+ years)',
    date: 'May 4, 2025',
    facility: 'Died in TransCor van en route to Stewart Detention Center, GA',
    cause: 'Suspected aortic aneurysm',
    detained_days: 25,
    story: 'A 68-year-old grandfather arrested on an alleged probation violation. Blood pressure reading of 226/57 — hypertensive crisis level — yet medical staff cleared him for transport. Found cold and stiff when EMS arrived, suggesting he had been dead far longer than the official timeline. TransCor is a CoreCivic subsidiary. His family said: "We want the truth."',
    source: 'The Appeal, Family Interviews'
  },
  {
    name: 'Francisco Gaspar-Andrés',
    age: 48,
    origin: 'Guatemala',
    date: 'December 3, 2025',
    facility: 'Camp East Montana, Fort Bliss, TX',
    cause: 'Liver failure (official: natural causes)',
    detained_days: 'Unknown',
    story: 'First person to die at the Fort Bliss tent city detention facility, which opened just months before. Civil rights groups had warned of inedible food, medical neglect, solitary confinement, beatings by masked officers, and abusive sexual contact. The same base held 100,000+ Japanese Americans during WWII.',
    source: 'The Appeal, Civil Rights Coalition'
  },
  {
    name: 'Geraldo Lunas Campos',
    age: 55,
    origin: 'Cuba (longtime U.S. resident, father of two)',
    date: 'January 3, 2026',
    facility: 'Camp East Montana, Fort Bliss, TX',
    cause: 'HOMICIDE — asphyxia from neck and torso compression',
    detained_days: 'Unknown',
    story: 'ICE claimed attempted suicide. The county medical examiner ruled it HOMICIDE — death by asphyxia from neck and torso compression by guards. A fellow detainee reported seeing guards choking Campos, who repeatedly said "I can\'t breathe" in Spanish. Civil rights groups had warned 26 days earlier that additional deaths were imminent if the camp continued to operate.',
    source: 'The Appeal, El Paso County Medical Examiner'
  },
  {
    name: 'Parady La',
    age: 46,
    origin: 'Cambodia',
    date: 'January 9, 2026',
    facility: 'Federal Detention Center, Philadelphia, PA',
    cause: 'Brain and organ failure from drug withdrawal',
    detained_days: 3,
    story: 'Arrested January 6 and dead three days later. Parady died of brain and organ failure following drug withdrawal — a preventable death with basic medical screening and treatment. Physicians for Human Rights found 95% of ICE custody deaths were preventable with appropriate care.',
    source: 'Al Jazeera, The Appeal'
  },
  {
    name: 'Victor Manuel Diaz',
    age: 36,
    origin: 'Nicaragua',
    date: 'January 18, 2026',
    facility: 'Camp East Montana, Fort Bliss, TX',
    cause: 'Presumed suicide (disputed by family)',
    detained_days: 'Unknown',
    story: 'Third death at the Fort Bliss facility in under two months. Arrested in Minnesota and transferred to the Texas tent city. ICE claimed he was found unconscious — his brother expressed disbelief. He is the second person to die at Fort Bliss where ICE claimed suicide, after the medical examiner ruled the first such claim a homicide.',
    source: 'The Appeal, Family Statement'
  }
];

// Global singleton
window.dataAPI = new DataAPI();
