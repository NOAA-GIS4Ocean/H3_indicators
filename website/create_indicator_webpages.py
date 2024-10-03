import geopandas as gpd
import numpy as np
import os

for i in range(1,7):
  url = "../data/indicators_all_res{}.geojson".format(i)

  gdf = gpd.read_file(url)
  gdf["log10(n)"] = np.log10(gdf["n"])

  m = gdf.explore(
     column = "log10(n)"
     )

  filename = url.split("/")[-1].replace(".geojson",".html")
  fout = os.path.join("deploy", filename)

  m.save(fout)