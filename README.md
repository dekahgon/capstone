# NYC Subway Network Analysis

This project analyzes the New York City subway GTFS data and builds a network graph of the system using Python, NetworkX, pandas, and Folium.

## Project structure

- `manhattan_network.py` — loads the GTFS data, builds the network graph, prints network metrics, and exports an interactive map to `nyc_subway.html`
- `ny_data/` — GTFS text files used as input data
- `nyc_subway.html` — generated interactive map
- `tests/` — regression tests for the script

## Requirements

This project uses Python 3.9+ and the following packages:

- pandas
- networkx
- folium
- numpy

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the analysis script:
   ```bash
   python manhattan_network.py
   ```
4. Run the tests:
   ```bash
   python -m unittest discover -s tests -v
   ```

## Notes

The repository includes a preconfigured `.venv/` directory for local development. For GitHub, the virtual environment is usually excluded from version control via `.gitignore`.
