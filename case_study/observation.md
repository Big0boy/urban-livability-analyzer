## Objective

The goal of the project was to evalute the livability of urban areas using public available **OpenStreetMap** and using **A\* pathfinding** wintin walking distance.I wanted to understand how well diffent cities perform in terms of **accessibility of green spaces,transport and essential servies**.

## Case Study Summary

> **Import things**

-   Each City was tested under same conditions that is with 100 sample points

-   **How to use the maps**:Click the layer icon in the top-right corner of the interactive map to toggle different data layers (e.g., green spaces, transit stops, livability scores).

**Pune,India**

<iframe src="case_study/maps/pune_india_advanced_map.html" width="800"height="600"></iframe>

```text
Green Access: 0.360
Transit Access: 0.230
Services Access: 0.387
Overall Livability: 0.326
High (≥0.7): 8.00%
Medium (0.4–0.7): 29.00%
Low (< 0.4): 63.00%
```

**observation:**

-   Transit stops are **highly centralized**, with **few connections to outer regions** of the city.
-   A significant number of sample points were located in undeveloped or inaccessible zones, which skewed the livability scores downward. -**Economically active areas** can be visually identified by dense clusters of banks, shops, and restaurants — mostly concentrated in city cores.
    -Green spaces are available but **not evenly distributed** in terms of access from all neighborhoods.
