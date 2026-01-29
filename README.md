# ICE Data Explorer

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

An interactive journalism-style dashboard for exploring U.S. immigration enforcement data, built with Dash/Plotly. This project aims to make immigration enforcement data accessible, transparent, and understandable to the public.

## Live Demo

🌐 **[View Live Site](https://ice-data-explorer.onrender.com)** *(Update with your deployed URL)*

## Features

### Data Visualizations
- **Interactive Charts**: Budget trends, detention population, deaths, deportations, costs
- **Geographic Maps**: Detention facilities, arrest hotspots, deportation flows
- **Narrative Sections**: Story-driven data exploration with scrollytelling
- **Taxpayer Receipt**: Calculate your personal tax contribution to enforcement

### Data Transparency
- **Full Data Explorer**: Query 23+ database tables with filtering, sorting, and CSV export
- **Source Badges**: Every statistic linked to verified sources with trust ratings
- **Methodology Notes**: Transparent documentation of data collection and limitations

### Technical Features
- **SQLite Backend**: Comprehensive database with data from multiple sources
- **Journalism-Style Design**: Clean, professional aesthetic inspired by NYT/Guardian visual journalism
- **Story Mode**: Immersive scrollytelling experience
- **Responsive Design**: Works on desktop and mobile

## Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ice-data-explorer.git
cd ice-data-explorer

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 app.py
```

Open **http://localhost:8050** in your browser.

## Deployment

### Deploy to Render (Free)

1. Fork this repository
2. Create a [Render account](https://render.com)
3. Click "New" → "Blueprint" → Connect your GitHub repo
4. Render will automatically detect `render.yaml` and deploy

The free tier includes:
- 750 hours/month of runtime
- Auto-deploy on git push
- Custom domains supported

### Alternative Platforms

- **Railway**: `railway up` (free tier available)
- **Fly.io**: `fly deploy` (free tier available)
- **PythonAnywhere**: Upload files via web interface

## Data Sources

| Source | Data Types |
|--------|------------|
| [ICE Official Statistics](https://www.ice.gov/statistics) | Detention, deportations, enforcement |
| [American Immigration Council](https://www.americanimmigrationcouncil.org) | Policy analysis, costs |
| [ACLU Reports](https://www.aclu.org) | Abuse documentation, deaths |
| [TRAC Immigration](https://trac.syr.edu) | Court data, enforcement trends |
| [Brennan Center for Justice](https://www.brennancenter.org) | Budget analysis |
| [USASpending.gov](https://www.usaspending.gov) | Contract data |
| [OpenSecrets](https://www.opensecrets.org) | Lobbying expenditures |

See `data/sources/` for complete source documentation.

## Key Statistics

| Statistic | Value | Source |
|-----------|-------|--------|
| 2025 Enforcement Budget | $170 billion | DHS Budget Justification |
| Current Detention Population | 73,000 | ICE Statistics |
| Detainees with No Criminal Record | 73% | TRAC Immigration |
| 2025 Custody Deaths | 32 | ICE/ACLU |
| Budget Increase Since 1994 | 765% | Brennan Center |
| Average Cost Per Deportation | $70,236 | American Immigration Council |

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Ways to Contribute
- 📊 **Data Updates**: Add new statistics with verified sources
- 📈 **Visualizations**: Create new charts or improve existing ones
- 🐛 **Bug Fixes**: UI improvements, error handling
- 📝 **Documentation**: Improve README, add data source docs
- 🌍 **Translations**: Help make the site multilingual
- ♿ **Accessibility**: Screen reader support, keyboard navigation

## Project Structure

```
ice-data-explorer/
├── app.py                 # Main Dash application
├── database.py            # Database setup and queries
├── pages/                 # Page modules
│   ├── narratives.py      # Story visualizations
│   ├── taxpayer_receipt.py
│   ├── memorial.py
│   └── ...
├── components/            # Reusable components
├── analysis/              # Statistical analysis
├── assets/                # CSS, JS, images
└── data/                  # Data files
```

## Tech Stack

- **[Dash](https://dash.plotly.com/)**: Web application framework
- **[Plotly](https://plotly.com/)**: Interactive visualizations
- **[SQLite](https://sqlite.org/)**: Database
- **[Pandas](https://pandas.pydata.org/)**: Data processing
- **[Bootstrap](https://getbootstrap.com/)**: UI components

## License

MIT License - See [LICENSE](LICENSE)

Data compiled from publicly available government and nonprofit sources for educational and journalistic purposes.

---

<p align="center">
  <strong>Making immigration enforcement data transparent and accessible</strong>
</p>
