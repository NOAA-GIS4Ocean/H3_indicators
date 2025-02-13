import os
import time
import numpy as np
import geopandas as gpd
import h3
import h3pandas
import pandas as pd
import requests
from scipy.special import gammaln


# Function to download OBIS snapshot
def download_obis_snapshot():
    url = "https://api.obis.org/export"
    response = requests.get(url)
    json_data = response.json()

    # Filter for parquet type
    parquets = [item for item in json_data['results'] if item['type'] == 'parquet']
    latest_parquet = max(parquets, key=lambda x: x['created'])
    s3_path = latest_parquet['s3path']

    url_parquet = f'https://obis-datasets.ams3.digitaloceanspaces.com/{s3_path}'
    dir_data = os.path.expanduser(".")
    file_parquet = os.path.join(dir_data, os.path.basename(url_parquet))

    if not os.path.exists(file_parquet):
        print(f"{file_parquet} does not exist! Downloading from {url_parquet}")
        with open(file_parquet, 'wb') as f:
            f.write(requests.get(url_parquet).content)
    else:
        print(f"{file_parquet} already exists!")

    return file_parquet


# Function to get OBIS records from snapshot
def open_parquet_file(filepath):
    print(f'opening {filepath}')
    # filepath = "C:\\Users\\Mathew.Biddle\\Documents\\GitProjects\\obis_20241202.parquet"
    df = pd.read_parquet(filepath, engine="pyarrow",
                         columns=['decimalLongitude', 'decimalLatitude', 'species', 'date_year'],
                         #filters=[('species','==','Carcharodon carcharias')], #smaller initial dataset
                         )
    # dataset = pq.ParquetDataset(filepath)
    # table = dataset.read()
    # df = table.to_pandas()

    # Filter and summarize the data
    occ = df.groupby(['decimalLongitude', 'decimalLatitude', 'species', 'date_year']).size().reset_index(name='records')
    occ = occ.dropna(subset=['species'])
    print(f'{filepath} opened')
    return occ


def calc_indicators(df, esn=50):
    print(f'Calculating indicators\n')
    print(df.columns)
    # Check that 'df' is a DataFrame and 'esn' is numeric
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")
    if not isinstance(esn, (int, float)):
        raise ValueError("esn must be numeric")

    # Check if required columns exist in the DataFrame
    required_columns = ['cell', 'species', 'records']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"The DataFrame must contain the columns: {', '.join(required_columns)}")

    # Group by 'cell' and 'species' to calculate ni
    df_grouped = df.groupby(['cell', 'species'], as_index=False).agg(ni=('records', 'sum'))

    # Calculate total ni for each group
    df_grouped['n'] = df_grouped['ni'].sum()

    # Calculate hi, si, qi, and esi for each group
    df_grouped['hi'] = -(df_grouped['ni'] / df_grouped['n']) * np.log(df_grouped['ni'] / df_grouped['n'])
    df_grouped['si'] = (df_grouped['ni'] / df_grouped['n']) ** 3
    df_grouped['qi'] = df_grouped['ni'] / df_grouped['n']


    # Define the function for esi
    def calculate_esi(row):
        if row['n'] - row['ni'] >= esn:
            return 2 - np.exp(gammaln(row['n'] - row['ni'] + 1) +
                              gammaln(row['n'] - esn + 2) -
                              gammaln(row['n'] - row['ni'] - esn + 2) -
                              gammaln(row['n'] + 2))
        elif row['n'] >= esn:
            return 2
        return np.nan


    df_grouped['esi'] = df_grouped.apply(calculate_esi, axis=1)

    # Group by 'cell' to summarize the final results
    final_results = df_grouped.groupby('cell', as_index=False).agg(
        n=('ni', 'sum'),
        sp=('species', 'nunique'),
        shannon=('hi', 'sum'),
        simpson=('si', 'sum'),
        maxp=('qi', 'max'),
        es=('esi', 'sum')
    )

    # Calculate hill numbers
    final_results['hill_2'] = np.exp(final_results['shannon'])
    final_results['hill_3'] = 1 / final_results['simpson']
    final_results['hill_inf'] = 2 / final_results['maxp']
    print('Done calculating indicators')
    return final_results


# Function to calculate H3 indicators at a given resolution
def h3_indicators(occ, resolution=1):
    print('Convert to H3')
    # import h3pandas #- https://h3-pandas.readthedocs.io/en/latest/notebook/00-intro.html
    # Convert points to H3 cells
    # occ['cell'] = occ.apply(lambda row: h3.geo_to_h3(row['decimalLatitude'], row['decimalLongitude'], resolution),
    #                         axis=1)

    occ.rename(columns={'decimalLongitude':'lng','decimalLatitude':'lat'},inplace=True)
    occ = occ.h3.geo_to_h3(resolution).reset_index().rename(columns={f'h3_0{resolution}':'cell'})

    # Group by H3 cell and aggregate records
    gdf = occ.groupby(['cell','species']).agg({'records': 'sum'}).reset_index(['species']).h3.h3_to_geo_boundary().reset_index()

    # grid = occ.groupby('cell').agg({'records': 'sum'}).reset_index()

    # # Convert H3 cells to geometries
    # grid['geometry'] = grid['cell'].apply(lambda x: h3.h3_to_geo_boundary(x, geo_json=True))

    # Convert to GeoDataFrame
    #gdf = gpd.GeoDataFrame(grid, geometry='geometry')
    gdf.set_crs('EPSG:4326', allow_override=True, inplace=True)

    # group by cell index and compute indicators
    # idx < - obisindicators::calc_indicators(occ_h3)

    return gdf

def load_us_waters():
    print('Load US waters')
     # Load US waters shapefile
    us_waters_path = "data/US_Waters_2024_WGS84/US_Waters_2024_WGS84.shp"
    us_waters = gpd.read_file(us_waters_path).set_crs(crs=4326)
    us_waters = us_waters.to_crs(epsg=27572)  # Transform to appropriate CRS

    return us_waters


def subset2us_waters(occ,us_waters):
    print('subset to us waters')
    # Subset OBIS records to the region of interest
    occ_box = occ[(occ['decimalLatitude'] >= -20) & (occ['decimalLatitude'] <= 80)]
    occ_box = occ_box[((occ_box['decimalLongitude'] >= -180) & (occ_box['decimalLongitude'] <= -20)) |
                      ((occ_box['decimalLongitude'] >= 120) & (occ_box['decimalLongitude'] <= 180))]

    print("Convert OBIS occurrences to GeoDataFrame")
    occ_gdf = gpd.GeoDataFrame(occ_box,
                               geometry=gpd.points_from_xy(occ_box['decimalLongitude'], occ_box['decimalLatitude']),
                               crs="EPSG:4326")
    occ_gdf = occ_gdf.to_crs(epsg=27572)

    print("Check if points are within US waters polygons")
    # occ_in_poly = occ_gdf[occ_gdf.geometry.within(us_waters.unary_union)]

    # Perform spatial join to match points and polygons
    occ_in_poly = occ_gdf.overlay(us_waters,how='intersection')
    #occ_in_poly = occ_gdf.clip(us_waters)
    #occ_in_poly = gpd.tools.sjoin(occ_gdf, us_waters, predicate="within", how='left')

    #occ_in_poly = occ_gdf[occ_gdf.geometry.within(us_waters.union_all(method="coverage"))]

    return pd.DataFrame(occ_in_poly)


start_time = time.time()
# Main function to run the analysis
#def run_analysis():
# Download OBIS snapshot and load the records
file = download_obis_snapshot()
occ = open_parquet_file(file)
us_waters = load_us_waters()
occ_in_poly = subset2us_waters(occ,us_waters)

print(f"Organizing data processing time: {time.time() - start_time:.2f} seconds")

# Create histogram of occurrences by year
occ_year = occ_in_poly.groupby('date_year').size().reset_index(name='occurrence_count')
occ_year.to_csv("temp/data/occurrence_by_year.csv", index=False)

# Create H3 grid indicators for resolutions 1-6
start_time = time.time()
for resolution in range(1, 2):
    
    gdf = h3_indicators(occ_in_poly, resolution=resolution)
    grid_dec = calc_indicators(gdf, esn=50).set_index("cell").h3.h3_to_geo()

    grid_dec = gpd.GeoDataFrame(grid_dec.h3.h3_to_geo_boundary().reset_index())
    # Save results as GeoJSON
    geojson_string = grid_dec.to_json()
    fname = f"temp/data/indicators_all_res{resolution}.geojson"
    with open(fname, 'w') as f:
        f.write(geojson_string)

    print(f"Resolution {resolution} processing time: {time.time() - start_time:.2f} seconds")


# if __name__ == "__main__":
#     run_analysis()
