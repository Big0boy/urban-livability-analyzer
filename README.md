# Urban Livability Analyzer

The Urban Livability Analyzer uses **OpenStreetMap (OSM)** data to assess the livability of urban areas based on access to green spaces, public transit,
and essential services. It calculates realistic walking distances using the **A\* algorithm** on the city’s street network.

---

## Features

-   Evaluates access to parks and recreational areas
-   Assesses proximity to transit stops
-   Considers services like healthcare, education, food, and banking
-   Uses A\* pathfinding for accurate distance-based scoring
-   Generates interactive Folium maps and GeoJSON/CSV output
-   Provides summary statistics for livability categories

---

## How It Works

1. Loads city boundaries and amenities using OSM via `osmnx`
2. Samples random points within the city
3. Snaps those points to a walkable street network
4. Measures accessibility to key services using A\* pathfinding
5. Calculates a livability score based on access to:
    - Green spaces
    - Transit
    - Services (with weighted importance)

---

## Getting Started

### 1. Clone The repository

```bash
git clone https://github.com/Big0boy/urban-livability-analyzer.git
cd urban-livability-analyzer
```

### 2.Install The Dependencies

```bash
pip install -r requirement.txt

```

### 3.Run The Analyzer

Edit the [`main.py`](main.py) as needed

```python
from src.config import AnalysisConfig
from src.analyzer import LivabilityAnalyzer

config = AnalysisConfig(
    cities=["Bhopal,India"],
    num_samples=100
)
analyzer = LivabilityAnalyzer(config)
analyzer.run()
```

Replace `"Bhopal, India"` with your city of choice. You can increase `num_samples` for better coverage—note that higher sample sizes require more time and memory.

`Then run:`

```bash
python main.py
```

---

## Outputs

-   `outputs/data/`: CSV + GeoJSON of sampled points and scores
-   `outputs/maps/`: Interactive HTML map
-   `outputs/reports`/: Summary of livability scores

---

## Additional Information

### Performance Notes

Livability analysis performance depends on the size and complexity of the city. These are rough estimates based on 100 sample points, tested on [Kaggle](www.kaggle.com) notebooks:

-   Bangalore, India: ~7 hours (large, complex road network)
-   Pune,India:~ 45 min

> For larger cities, increase in sample size or services density may significantly impact runtime and memory usage. A machine with **16GB+ RAM** is recommended for very large urban areas.

### Case Studies

Real-world case studies and their corresponding output files are available in the [`case_study/`](case_study/) folder.

Each case study includes:

-   Generated maps
-   Output GeoJSON and CSV
-   Summary reports

It also includes personal insights and reflections in [`observation.md`](case_study/observation.md)

---

## Acknowledgements

Build using:

-   [OpenStreetMap](https://www.openstreetmap.org/)
-   [Leaflet](https://leafletjs.com/)
-   [Folium](https://python-visualization.github.io/folium/)

---

## Things I'd like to Improve

-   Sometimes the samplepoints are taken at random parks and empty areas with no roads which causes the average to go down.
-   Using population heatmap to influence the sample points
-   Improving the program and make it more efficient

---
