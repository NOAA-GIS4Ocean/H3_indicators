# H3_indicators
Notebooks and documentation about computing biodiversity indicators from the [Ocean Biodiversity Information System (OBIS)](https://obis.org/) snapshots (periodic full exports of the OBIS database) on [H3 grids](https://h3geo.org/docs).

## 💾 Source data
The data sourced for this effort comes from the publicly available OBIS snapshots, which can be found at https://api.obis.org/export.

## ❓ What's in this repo?

* `GIS4Ocean_h3_indicators.Rmd` -
   * downloads the most recent snapshot,
   * clips the data to US Waters as identified in the [shapefiles](https://github.com/NOAA-GIS4Ocean/H3_indicators/tree/main/data/US_Waters_2024_WGS84).
   * grids the data to a determined [H3 grid resolution](https://h3geo.org/docs/core-library/restable/),
   * computes various indicators using the [`obisindicators`](https://marinebon.github.io/obisindicators/) R package,
   * saves the results to `.geojson` files in the `data/` directory.
* `read_and_plot_geojson_heatmap.ipynb`
   * takes the resultant `.geojson` files and saves them as html interactive maps

Manually, the `.html` interactive maps are then served via GitHub Pages in the `gh-pages` branch. To view the interactive maps, browse to https://noaa-gis4ocean.github.io/H3_indicators/.

Testing GH-Actions currently.

## 🖐️ Want to help out?
* Check out our [CONTRIBUTING GUIDE](https://github.com/NOAA-GIS4Ocean/H3_indicators/blob/main/CONTRIBUTING.md) for more details.
