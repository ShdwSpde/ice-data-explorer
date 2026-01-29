# Contributing to ICE Data Explorer

Thank you for your interest in contributing to this project. This data transparency initiative aims to make immigration enforcement data accessible and understandable to the public.

## Getting Started

### Prerequisites
- Python 3.11+
- pip or conda for package management

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ice-data-explorer.git
   cd ice-data-explorer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the development server**
   ```bash
   python app.py
   ```
   The app will be available at `http://127.0.0.1:8050`

## Project Structure

```
ice-data-explorer/
├── app.py                 # Main Dash application
├── database.py            # SQLite database setup and queries
├── pages/                 # Page-specific content modules
│   ├── narratives.py      # Narrative visualizations
│   ├── taxpayer_receipt.py # Tax contribution calculator
│   ├── memorial.py        # Memorial page
│   └── ...
├── components/            # Reusable visualization components
├── analysis/              # Statistical analysis modules
├── assets/                # CSS, JavaScript, images
│   ├── style.css          # Main stylesheet
│   └── wow-features.js    # Interactive features
└── data/                  # Data files and sources
```

## How to Contribute

### Reporting Issues
- Use GitHub Issues to report bugs or suggest features
- Include screenshots for UI issues
- Provide steps to reproduce bugs

### Submitting Changes

1. **Fork the repository**

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test locally before submitting

4. **Commit with clear messages**
   ```bash
   git commit -m "Add: description of what you added"
   git commit -m "Fix: description of what you fixed"
   git commit -m "Update: description of what you changed"
   ```

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Types of Contributions Welcome

- **Data Updates**: New or updated statistics with verified sources
- **Visualizations**: New charts, maps, or interactive elements
- **Bug Fixes**: UI/UX improvements, error handling
- **Documentation**: README updates, code comments, data source documentation
- **Accessibility**: Improving screen reader support, color contrast, keyboard navigation
- **Translations**: Multi-language support
- **Performance**: Optimization, caching improvements

## Data Standards

### Source Requirements
All data must include:
- Primary source citation
- Date of data collection/publication
- Methodology notes where applicable
- Trust level classification (Official, Verified Independent, Investigative, etc.)

### Adding New Data
1. Add source documentation to `data/sources/`
2. Update database schema in `database.py` if needed
3. Create or update visualization in appropriate `pages/` module
4. Add data transparency badges per project standards

## Code Style

- Use Python type hints where practical
- Follow PEP 8 guidelines
- Use meaningful variable names
- Keep functions focused and documented

## Testing

Before submitting:
```bash
# Check for Python errors
python -c "from app import app; print('App loads successfully')"

# Test specific pages
python -c "from pages.narratives import *; print('Narratives OK')"
```

## Questions?

Open an issue with the "question" label or reach out to maintainers.

## Code of Conduct

- Be respectful and constructive
- Focus on facts and data
- Welcome diverse perspectives
- Maintain journalistic integrity in data presentation

---

Thank you for helping make immigration enforcement data more transparent and accessible.
