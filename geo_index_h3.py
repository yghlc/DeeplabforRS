#!/usr/bin/env python
# Filename: geo_index_h3.py 
"""
introduction:  using Uber's H3 Hexagonal Hierarchical Geospatial Indexing System

github (python): https://github.com/uber/h3?tab=readme-ov-file
site: https://h3geo.org/docs/

authors: Huang Lingcao
email:huanglingcao@gmail.com
add time: 24 July, 2025
"""

import h3
import geopandas as gpd

def get_h3_cell_id(latitude, longitude, resolution):
    """
    Given a latitude, longitude, and H3 resolution, return the H3 cell ID as a string.
    Args:
        latitude (float): Latitude in decimal degrees.
        longitude (float): Longitude in decimal degrees.
        resolution (int): H3 resolution (0-15), refer to: https://h3geo.org/docs/core-library/restable
    Returns:
        str: H3 cell ID.
    """
    return h3.latlng_to_cell(latitude, longitude, resolution)

def test_get_h3_cell_id():
    # for res in range(0,16):
    #     cell_id = get_h3_cell_id(37.775938728915946, -122.41795063018799, res)
    #     print(res,':',cell_id)  # e.g., '87283082bffffff'

    lat1, lng1 = 75.0, -42.0
    lat2, lng2 = 75.0005, -42.0005  # Very close by
    cell1 = h3.latlng_to_cell(lat1, lng1, 7)
    cell2 = h3.latlng_to_cell(lat2, lng2, 7)
    print(cell1)
    print(cell2)
    print(cell1 == cell2)  # True if they're in the same H3 cell



def main():
    test_get_h3_cell_id()
    pass


if __name__ == '__main__':
    main()
