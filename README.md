# H3_indicators
Notebooks and documentation about computing biodiversity indicators from the [Ocean Biodiversity Information System (OBIS)](https://obis.org/) snapshots (periodic full exports of the OBIS database) on [H3 grids](https://h3geo.org/docs).

![image](https://github.com/user-attachments/assets/c5adee31-153d-4ac8-95a2-5ebd93fd3476)

## 💾 Source data
The data sourced for this effort comes from the publicly available OBIS snapshots, which can be found at https://api.obis.org/export.

## ❓ What's in this repo?

* `GIS4Ocean_h3_indicators.Rmd`
   * downloads the most recent snapshot,
   * clips the data to US Waters as identified in the [shapefiles](https://github.com/NOAA-GIS4Ocean/H3_indicators/tree/main/data/US_Waters_2024_WGS84).
   * grids the data to a determined [H3 grid resolution](https://h3geo.org/docs/core-library/restable/),
   * computes various indicators using the [`obisindicators`](https://marinebon.github.io/obisindicators/) R package,
   * saves the results to `.geojson` files in the `data/` directory.
* `GIS4Ocean_h3_indicators.R`
  * Same as above but in an R script file instead of Rmarkdown. In an attempt to simplify the infrastructure needed to run the code (ie. remove requirement to run Rmarkdown files)
* `GIS4Ocean_h3_indicators.ipynb` 
  * **Work In Progress**: _Draft_ conversion of the R code above into Python for use in cloud computing infrastructure (eg. Dask).
* `read_and_plot_geojson_heatmap.ipynb`
   * Example notebook showing how to read geojson files and plot the data on an interactive map.
* `data/`
  * Output `.geojson` indicator files at various resolutions.
  * Includes shapefile for "US Waters".
* `website/`:
  * `create_indicator_webpages.py` reads `.geojson` data and creates an html map to serve on the GitHub Pages website.

## 👁️Where can I see the results?
The resultant data are served as interactive maps at https://noaa-gis4ocean.github.io/H3_indicators/.

The maps are generated via [GitHub Action](https://github.com/NOAA-GIS4Ocean/H3_indicators/blob/main/.github/workflows/website_create_and_deploy.yml) which update everytime a file is changed in `data/`.

## 🖐️ Want to help out?
* Check out our [CONTRIBUTING GUIDE](https://github.com/NOAA-GIS4Ocean/H3_indicators/blob/main/CONTRIBUTING.md) for more details.

## Repository citation
[![DOI](https://zenodo.org/badge/852883236.svg)](https://doi.org/10.5281/zenodo.15113966)
