# README

This directory contains biodiversity indicator files on an [H3 grid](https://h3geo.org/).

The indicators were developed using the R [obisindicators](https://github.com/marinebon/obisindicators) package.

The source data are from the OBIS snapshot `obis_20240723.parquet`.

The filename convention is as follows: indicators_all_res[resolution].geojson

where, 

   [resolution] = the H3 grid resolution.
   
These files were generated from the script:
* https://github.com/NOAA-GIS4Ocean/H3_indicators/blob/main/GIS4Ocean_h3_indicators.Rmd

