## Functions in this file are used to transform & analyze rainfall data.

# IMPORTS
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
from geopy.geocoders import Nominatim as geonom


def get_resampled_rainfall(rf_csv, rez="D", out_file=None, geoout=True):
    # Arguments: 
    # rf_csv - Name of the input csv containing rainfall data
    #    CSV is expected to contain longitude, latitude, time, and value column
    # rez - The time resolution we want to resample to. Original data is hourly.
    #    This can be daily, monthly, or annually ("D", "M", "Y")
    # out_file - [optional] The name of the csv file to which we want to store the
    #    results. If not specified, the data will just be returned and not written.
    
    # Read the data into a Pandas Dataframe
    rfpd = pd.read_csv(rf_csv)
    rfpd["time"] = pd.to_datetime(rfpd["time"])
    
    rfpd = rfpd.set_index(["latitude", "longitude", "time"])
    
    # Get the mean rainfall at the specified resolution
    group = ["latitude", "longitude",
             pd.Grouper(freq=rez, level=2)]
    rfmean = (rfpd.groupby(group).mean())
    
    tosave = rfmean.reset_index()
    
    # Save results in format matching original
    if out_file is not None:
        tosave.to_csv(out_file)
    
    # Provide dataframe in convenient format for visualizing time series
    if geoout:
        points = gpd.points_from_xy(tosave.longitude, tosave.latitude)
        gdf = gpd.GeoDataFrame(tosave,
                               geometry=points,
                               crs="EPSG:4326")
        gdf = gdf.drop(["longitude", "latitude"], axis=1)
        return gdf
    else:
        tosave["lat_long"] = list(zip(tosave["latitude"], tosave["longitude"]))
        tosave = tosave.drop(["longitude", "latitude"], axis=1)\
                       .set_index(["lat_long", "time"])
        return  tosave.sort_values(["lat_long", "time"])