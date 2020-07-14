#!/usr/bin/env python
# Filename: read_raster_for_shapefile.py
"""
introduction:

authors: Yan
email: yan_hu@hotmail.com
add time: 29 July, 2018
"""

import os, sys, math
from optparse import OptionParser
import basic_src
from basic_src import io_function
from basic_src import basic
from basic_src import RSImage

import shapefile
import vector_features

from vector_features import shape_opeation

import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import numpy as np
import scipy.integrate as integrate
from scipy.integrate import quad
import geopy.distance


def read_start_end_point_length_of_a_line(shape_file):
    """

    Args:
        shape_file:

    Returns:

    """

    if io_function.is_file_exist(shape_file) is False:
        return False

    try:
        org_obj = shapefile.Reader(shape_file)
    except:
        basic.outputlogMessage(str(IOError))
        return False

    # Create a new shapefile in memory
    # w = shapefile.Writer()
    # w.shapeType = org_obj.shapeType

    org_records = org_obj.records()
    if (len(org_records) < 1):
        basic.outputlogMessage('error, no record in shape file ')
        return False

    # Copy over the geometry without any changes
    shapes_list = org_obj.shapes()
    if len(shapes_list) < 1:
        raise ValueError("No shape")

    # define list
    start_point = []
    end_point = []
    length = []

    # read length (second)
    for record in org_records:
        length.append(record[1])

    for shape in shapes_list:
        # print(shape)
        # print(shape)
        print(shape.points)
        points = shape.points
        if len(points) != 2:
            raise ValueError("Not 2 points in a line")

        start_point.append(points[0])
        end_point.append(points[1])

    return start_point, end_point, length


def read_dem_basedON_location(x, y, dem_raster):
    # return RSImage.get_image_location_value(dem_raster,x,y,'lon_lat_wgs84',1)
    return RSImage.get_image_location_value(dem_raster, x, y, 'lon_lat_wgs84', 1)

def read_phs_basedON_location(x1, y1, x2, y2, x3, y3, phs_raster):

    refs = []

    ref1 = read_dem_basedON_location(x1, y1, phs_raster)
    if ref1 != -9999:
        refs.append(ref1)
    ref2 = read_dem_basedON_location(x2, y2, phs_raster)
    if ref2 != -9999:
        refs.append(ref2)
    ref3 = read_dem_basedON_location(x3, y3, phs_raster)
    if ref3 != -9999:
        refs.append(ref3)
    ref = np.mean(refs)

    return ref, ref1, ref2, ref3


def calculate_polygon_velocity(polygons_shp, vel_file):
    """

    Args:
        polygons_shp:
        dem_file:

    Returns:

    """
    if io_function.is_file_exist(polygons_shp) is False:
        return False
    operation_obj = shape_opeation()

    # all_touched: bool, optional
    #     Whether to include every raster cell touched by a geometry, or only
    #     those having a center point within the polygon.
    #     defaults to `False`
    #   Since the dem usually is coarser, so we set all_touched = True
    all_touched = True

    # #DEM
    if io_function.is_file_exist(vel_file):
        stats_list = ['min', 'max', 'mean', 'median', 'std']  # ['min', 'max', 'mean', 'count','median','std']
        if operation_obj.add_fields_from_raster(polygons_shp, vel_file, "vel", band=1, stats_list=stats_list,
                                                all_touched=all_touched) is False:
            return False
    else:
        basic.outputlogMessage("warning, VEL file not exist, skip the calculation of VEL information")

    return True


def caluculate_geometry_from_creep_line(shp_file, dem_file, save_path):

    # shp and dem files are in lon lat coordinates

    # read shape file
    lines = gpd.read_file(shp_file)
    line_count = lines['Name'].count()
    name = []

    # get value of points
    start_point, end_point, length = read_start_end_point_length_of_a_line(shp_file)

    for idx in range(line_count):

        name.append(lines['Name'][idx])
        # read value of start point
        start_value = read_dem_basedON_location(start_point[idx][0], start_point[idx][1], dem_file)
        # read value of end point
        end_value = read_dem_basedON_location(end_point[idx][0], end_point[idx][1], dem_file)

        h = start_value - end_value

        # calculate bearing of line/aspect of RGs; from lon and lat
        lat1 = math.radians(start_point[idx][1])
        lat2 = math.radians(end_point[idx][1])
        diffLong = math.radians(end_point[idx][0] - start_point[idx][0])
        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        asp_deg = (initial_bearing + 360) % 360
        asp_rad = math.radians(asp_deg)

        d = geopy.distance.vincenty((start_point[idx][0], start_point[idx][1]), (end_point[idx][0], end_point[idx][1])).m
        slp_rad = math.atan(h / d)
        slp_deg = math.degrees(slp_rad)

        print(name[idx],start_value, end_value, h, d, slp_deg, asp_deg)

        out_file_name = str(save_path) + "/TARGET_info.list"
        line_result = open(out_file_name, 'a')
        line_result.write(str(name[idx]) + ' ' + str(slp_rad) + ' ' + str(asp_rad) + ' ' + str(h) + ' ' + str(d) + '\n')
        line_result.close()

def calculate_line_aspect(shp_file, dem_file, save_path):
    # read shape file
    start_point, end_point, length = read_start_end_point_length_of_a_line(shp_file)

    # get value of points
    shape_count = len(start_point)


    for idx in range(shape_count):
        # read value of start point
        start_value = read_dem_basedON_location(start_point[idx][0], start_point[idx][1], dem_file)
        # read value of end point
        end_value = read_dem_basedON_location(end_point[idx][0], end_point[idx][1], dem_file)

        #print(start_value, end_value)

        # calculate bearing of line/aspect of RGs; from lon and lat
        lat1 = math.radians(start_point[idx][1])
        lat2 = math.radians(end_point[idx][1])
        diffLong = math.radians(end_point[idx][0] - start_point[idx][0])
        x = math.sin(diffLong) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
        initial_bearing = math.atan2(x, y)
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        print(idx + 1,start_value, end_value, compass_bearing)


        out_file_name = str(save_path) + "LINE_RESULT.csv"
        line_result = open(out_file_name, 'a')
        line_result.write(str(start_value) + ',' + str(end_value) + ',' + str(compass_bearing) + '\n')
        line_result.close()
    pass

def cal_vel_error(file_path, shp_file, target_info_list, position_error, dem_error, sensor, PF_name, dates, wavelen, span, N, out_file_name, threshold):
# produce (1) the clipped vel raster for each target
#         (2) the csv file to record the statistics of each target

## a sample TARGET_info.list is produced by caluculate_geometry_from_creep_line
# TARGET_name   slope_angle_rad    aspect_angle_rad   h     d
# Kongma               0.3               0.5         100   1000

    IFG_name = str(PF_name) + '.' + str(dates)

    shapefile = gpd.read_file(shp_file)
    geoms = shapefile.geometry.values

    # n_row = shapefile['Name'].count()
    # name = []
    #
    # for r in range(n_row):
    #     name.append(shapefile['Name'][r])
    #
    # print('From shp:', name)

    # name_list = []
    with open(target_info_list, "r") as info_file:
        shp_count = 0
        for line_t in info_file:
            fields_t = line_t.split()
            TARGET_name = fields_t[0]
            print(TARGET_name)
            # name_list.append(TARGET_name)


            slp_angle = float(fields_t[1])
            asp_ori = float(fields_t[2])
            h = float(fields_t[3])
            d = float(fields_t[4])

            vel_file = file_path + "/" + str(IFG_name) + "_VEL_rasters_" + str(threshold) + "/" + str(TARGET_name) + "_vel"
            coh_file = file_path + "/" + str(IFG_name) + "_COH_rasters_" + str(threshold) + "/" + str(TARGET_name) + "_coh"
            inc_file = file_path + "/" + str(IFG_name) + "_INC_rasters_" + str(threshold) + "/" + str(TARGET_name) + "_inc"
            azi_file = file_path + "/" + str(IFG_name)+ "_AZI_rasters_" + str(threshold) + "/" + str(TARGET_name) + "_azi"
            vel_los_file = file_path + "/" + str(IFG_name) + "_LOS_rasters_" + str(threshold) + "/" + str(TARGET_name) + "_los"
            unmasked_coh_file = file_path + "/" + str(IFG_name) + "_coh_map"

            #read coh value of one shape from the coherence raster, inc raster, los azimuth raster into arrays
            geoms_shp = [mapping(geoms[shp_count])]

            with rasterio.open(coh_file) as src_coh:
                out_coh, out_coh_transform = mask(src_coh, geoms_shp, all_touched=True, crop=True)

            with rasterio.open(inc_file) as src_inc:
                out_inc, out_inc_transform = mask(src_inc, geoms_shp, all_touched=True, crop=True)

            with rasterio.open(azi_file) as src_azi:
                out_azi, out_azi_transform = mask(src_azi, geoms_shp, all_touched=True, crop=True)

            with rasterio.open(vel_los_file) as src_vel_los:
                out_vel_los, out_vel_los_transform = mask(src_vel_los, geoms_shp, all_touched=True, crop=True)

            with rasterio.open(unmasked_coh_file) as src_unmasked_coh:
                out_unmasked_coh, out_unmasked_coh_transform = mask(src_unmasked_coh, geoms_shp, all_touched=True, crop=True)

            with rasterio.open(vel_file) as src_vel:
                out_vel, out_vel_transform = mask(src_vel, geoms_shp, all_touched=True, crop=True)

            out_meta = src_vel.meta.copy()
            out_meta.update({"driver": "GTiff",
                              "height": out_vel.shape[1],
                              "width": out_vel.shape[2],
                              "transform": out_vel_transform})
            image_name = str(file_path) + "/" + str(IFG_name) +"_VEL_clipped_" + str(threshold) + "/" + str(TARGET_name) + '_' + str(IFG_name) + "_vel_ap.tif"
            with rasterio.open(image_name, "w", **out_meta) as dest:
                dest.write(out_vel)

            no_data_coh = src_coh.nodata
            no_data_inc = src_inc.nodata
            no_data_azi = src_azi.nodata
            no_data_vel_los = src_vel_los.nodata
            no_data_unmasked_coh = 0
            no_data_vel = src_vel.nodata

            # extract the values of the masked array
            data_coh = out_coh[0]
            data_inc = out_inc[0]
            data_azi = out_azi[0]
            data_vel_los = out_vel_los[0]
            data_unmasked_coh = out_unmasked_coh[0]
            data_vel = out_vel[0]

            # extract the valid values
            coh = np.extract(data_coh != no_data_coh, data_coh)
            inc = np.extract(data_inc != no_data_inc, data_inc)
            azi = np.extract(data_azi != no_data_azi, data_azi)
            vel_los = np.extract(data_vel_los != no_data_vel_los, data_vel_los)
            unmasked_coh = np.extract(data_unmasked_coh != no_data_unmasked_coh, data_unmasked_coh)
            vel = np.extract(data_vel != no_data_vel, data_vel)
            # print(vel)


            #calculate downslope velocity error for each pixel and store into array
            error_d = position_error * math.sqrt(2)
            error_h = dem_error * math.sqrt(2)

            d_vel_los = 1 / (np.cos(inc) * np.sin(slp_angle) - np.cos(asp_ori + azi))
            error_phs = (1 / math.sqrt(2 * N)) * (np.sqrt(1 - np.power(coh, 2)) / coh)
            error_vel_los = error_phs * (wavelen / (4 * np.pi)) * (365 / span)

            d_slp_angle = (- vel_los * np.cos(inc) * math.cos(slp_angle)) / np.power((np.cos(inc) * np.sin(slp_angle) - np.cos(asp_ori + azi)), 2)
            error_slp_angle = math.sqrt(((error_h * d) / (d ** 2 + h ** 2)) ** 2 + (error_d * h / (d ** 2 + h ** 2)) ** 2)

            d_asp_ori = (- vel_los * np.sin(asp_ori + azi)) / np.power((np.cos(inc) * math.sin(slp_angle) - np.cos(asp_ori + azi)), 2)
            error_asp_ori = error_d / d

            error_vel_slp = np.sqrt((np.power((d_vel_los * error_vel_los), 2)) + (np.power((d_slp_angle * error_slp_angle), 2)) + (np.power((d_asp_ori * error_asp_ori), 2)))

            #calculate the error of the mean velocity for all the pixels
            if len(vel) == 0:
                vel_mean = vel_median = vel_max = vel_std = error_mean_vel = error_max_vel = error_median_vel = -9999
                coh_mean = ratio = 0
                print(vel_mean, error_mean_vel, vel_median, error_median_vel, vel_max, error_max_vel, vel_std)
                print(coh_mean, ratio)
            else:
                vel_mean = np.around(np.mean(vel), 2)
                vel_median = np.around(np.median(vel), 2)
                vel_max = np.around(np.max(vel), 2)
                vel_std = np.around(np.std(vel), 2)

                error_mean_vel = np.around((1 / vel_los.size) * np.sqrt(np.sum(error_vel_slp ** 2)), 2)
                #index_median = np.argsort(vel)[len(vel)//2]
                index_median = np.argmin(np.abs(np.median(vel)-vel))
                error_median_vel = np.around(error_vel_slp[index_median], 2)
                index_max = vel.argmax()
                error_max_vel = np.around(error_vel_slp[index_max], 2)
                print(vel_mean, error_mean_vel, vel_median, error_median_vel, vel_max, error_max_vel, vel_std)

                coh_mean = np.around(np.mean(unmasked_coh), 2)
                ratio = np.around(np.size(coh) / np.size(unmasked_coh), 2)
                print(coh_mean, ratio)

            result = open(out_file_name, 'a')
            result.write(str(sensor) + ',' + str(PF_name) + ',' + str(dates) + ',' + str(TARGET_name) + ','
                         + str(vel_mean) + ',' + str(error_mean_vel) + ','
                         + str(vel_max) + ',' + str(error_max_vel) + ','
                         + str(vel_median) + ',' + str(error_median_vel) + ','
                         + str(vel_std) + ',' + str(coh_mean) + ',' + str(ratio) + '\n')
            result.close()
            shp_count = shp_count + 1
        # print('From list:', name_list)


def cal_polygon_phs_uncertainty(shp_file, phs_file, coh_file):

    #read phs value and coh value from the wrapped phs raster into array
    shapefile = gpd.read_file(shp_file)
    geoms = shapefile.geometry.values
    geoms = [mapping(geoms[0])]

    with rasterio.open(phs_file) as src_phs:
        out_phs, out_phs_transform = mask(src_phs, geoms, crop=True)

    with rasterio.open(coh_file) as src_coh:
        out_coh, out_coh_transform = mask(src_coh, geoms, crop=True)

    no_data_phs = src_phs.nodata
    no_data_coh = src_coh.nodata

    # extract the values of the masked array
    data_phs = out_phs[0]
    #data_phs = out_phs.reshape(out_phs.shape[1:])
    data_coh = out_coh[0]

    # extract the valid values
    phs = np.extract(data_phs != no_data_phs, data_phs)
    coh = np.extract(data_coh != no_data_coh, data_coh)

    # calculate the pdf for the polygon
    phs_mean = np.mean(phs)
    coh_mean = np.mean(coh)
    print(coh_mean)
    #beta = coh * np.cos(phs - phs_mean)
    L = 10
    #item1 = np.power((1 - np.power(coh, 2)), L) / (2 * np.pi)
    item2 = math.gamma(2 * L - 1) / (np.power(math.gamma(L), 2) * np.power(2, 2 * (L - 1)))
    #item3 = ((2 * L - 1) * beta) / np.power((1 - np.power(beta, 2)), L + 1/2)
    #item4 = np.pi/2 + np.arcsin(beta)
    #item5 = 1 / np.power((1 - np.power(beta, 2)), L)
    item6 = 1 / (2 * (L - 1))
    #item7 = 0
    #for k in range(L - 1):
    #    item7_1 = math.gamma(L - 1/2) / math.gamma(L - 1/2 - k)
    #    item7_2 = math.gamma(L - 1 - k) / math.gamma(L - 1)
    #    item7_3 = (1 + (2 * k + 1) * np.power(beta, 2)) / np.power((1 - np.power(beta, 2)), (k + 2))
    #    item7 = item7_1 * item7_2 * item7_3 + item7
    #pdf = item1 * (item2 *(item3 * item4 + item5) + item6 * item7)

    #calculate the phs variance of the polygon
    var_phs = np.empty(coh.size)
    std_phs = np.empty(coh.size)
    for i in range(coh.size):
        integrand = lambda x: np.power((x - phs_mean), 2) * ((np.power((1 - np.power(coh[i], 2)), L) / (2 * np.pi)) * (item2 * ((((2 * L - 1) * (coh[i] * np.cos(x - phs_mean))) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), L + 1/2)) * (np.pi/2 + np.arcsin(coh[i] * np.cos(x - phs_mean))) + (1 / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), L))) + item6 * (((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 0)) * (math.gamma(L - 1 - 0) / math.gamma(L - 1)) * ((1 + (2 * 0 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (0 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 1)) * (math.gamma(L - 1 - 1) / math.gamma(L - 1)) * ((1 + (2 * 1 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (1 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 2)) * (math.gamma(L - 1 - 2) / math.gamma(L - 1)) * ((1 + (2 * 2 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (2 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 3)) * (math.gamma(L - 1 - 3) / math.gamma(L - 1)) * ((1 + (2 * 3 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (3 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 4)) * (math.gamma(L - 1 - 4) / math.gamma(L - 1)) * ((1 + (2 * 4 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (4 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 5)) * (math.gamma(L - 1 - 5) / math.gamma(L - 1)) * ((1 + (2 * 5 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (5 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 6)) * (math.gamma(L - 1 - 6) / math.gamma(L - 1)) * ((1 + (2 * 6 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (6 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 7)) * (math.gamma(L - 1 - 7) / math.gamma(L - 1)) * ((1 + (2 * 7 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (7 + 2)))) + ((math.gamma(L - 1/2) / math.gamma(L - 1/2 - 8)) * (math.gamma(L - 1 - 8) / math.gamma(L - 1)) * ((1 + (2 * 8 + 1) * np.power((coh[i] * np.cos(x - phs_mean)), 2)) / np.power((1 - np.power((coh[i] * np.cos(x - phs_mean)), 2)), (8 + 2)))))))
        result = quad(integrand, -np.pi, np.pi)
        var_phs[i] = result[0]
        std_phs[i] = np.sqrt(var_phs[i])
    var_phs_mean = np.mean(var_phs)
    std_phs_mean = np.mean(std_phs)

    print(var_phs_mean)
    print(std_phs_mean, '\n')


def main(options, args):
#########calculate line aspect###########
    # shp_file = "/home/huyan/huyan_data/khumbu_valley/shp/Khumbu_creep_lines_lonlat.shp"
    # dem_file = "/home/huyan/huyan_data/SRTM/khumbu_valley/khumbu_dem_deg.tif"
    # save_path = "/home/huyan/huyan_data/khumbu_valley/alos/result"
    #
    # caluculate_geometry_from_creep_line(shp_file, dem_file, save_path)
    #

#########

#    file_path = args[0]

#    with open(file_path + "/ARG_info.list", "r") as info_file:
#        for line in info_file:
#            fields = line.split()
#            PF_name = fields[0]
#            ARG_name = fields[1]
#            print(ARG_name)
#            shp_file = file_path + "/shpfiles/polygons/" + str(ARG_name) + ".shp"
#            vel_file = file_path + "/VEL_rasters/" + str(ARG_name) + "_vel"
#            coh_file = file_path + "/COH_rasters/" + str(ARG_name) + "_coh"
#            inc_file = file_path + "/INC_rasters/" + str(ARG_name) + "_inc"
#            azi_file = file_path + "/AZI_rasters/" + str(ARG_name) + "_azi"
#            vel_los_file = file_path + "/LOS_rasters/" + str(ARG_name) + "_los"
#            unmasked_coh_file = file_path + "/" + PF_name + ".coh_map"
#            asp_ori = float(fields[5])
#            slp_angle = float(fields[4])
#            h = float(fields[6])
#            d = float(fields[7])
#            save_path = file_path
#            N = 10
#            position_error = 50
#            dem_error = 16
#            wavelen = 23.60571
            ##wavelen = 24.24525
#            span = 46

 #           cal_vel_error(ARG_name, PF_name, save_path, shp_file, coh_file, inc_file, azi_file, vel_los_file,
 #                         unmasked_coh_file, vel_file, asp_ori, slp_angle, h, d,
 #                         N, wavelen, span, position_error, dem_error)

##########jingxian lobe/time series instead of snapshot############
## a sample IFG.list
# Sensor    PF_name            dates       span  wavelen  number_of_azimuth_looks  number_of_range_looks
# ALOS      P507_F540   20071213_20080128   46   23.0571             4                    9
#
    file_path = "/home/huyan/huyan_data/khumbu_valley/alos2/result"
    shp_file = "/home/huyan/huyan_data/khumbu_valley/shp/Khumbu_targets_lonlat_rs.shp"
    ifg_list = file_path + "/IFG_2.list"
    target_info_list = file_path + "/TARGET_info_2.list"
    out_file_name = file_path + "/VEL_RESULT_2_ap.csv"
    threshold = 5
    position_error = 50
    # SRTM: 16; TANDEM: 10
    dem_error = 16

    result = open(out_file_name, 'a')
    result.write('Sensor' + ',' + 'Path_Frame' + ',' + 'Dates' + ',' + 'Target_name' + ','
                 + 'Mean_velocity' + ',' + 'Error_Vmean' + ','
                 + 'Max_velocity' + ',' + 'Error_Vmax' + ','
                 + 'Median_velocity' + ',' + 'Error_Vmed' + ','
                 + 'Std' + ',' + 'Mean_coherence' + ',' + 'Ratio' + '\n')
    result.close()

    with open(ifg_list, "r") as ifg_file:
        for line_ifg in ifg_file:

            fields_ifg = line_ifg.split()
            sensor = fields_ifg[0]
            PF_name = fields_ifg[1]
            dates = fields_ifg[2]
            span = int(fields_ifg[3])
            wavelen = float(fields_ifg[4])
            n_azi = int(fields_ifg[5])
            n_range = int(fields_ifg[6])

            N = n_azi * n_range

            cal_vel_error(file_path, shp_file, target_info_list, position_error, dem_error, sensor, PF_name, dates, wavelen, span, N, out_file_name, threshold)
#
# #################cal ref value###################
#     RESULT_DIR = "/home/huyan/huyan_data/khumbu_valley/alos2/result"
#
#     IFG_list = RESULT_DIR + "/IFG_2.list"
#     position_list = RESULT_DIR + "/ref_position_2.list"
#     out_file_name = RESULT_DIR + "/REF_2.list"
#
#     with open(position_list, "r") as info_file:
#         for line_target in info_file:
#             fields_target = line_target.split()
#             TARGET_name = fields_target[0]
#             print(TARGET_name)
#             ref_lon1 = fields_target[1]
#             ref_lat1 = fields_target[2]
#             ref_lon2 = fields_target[3]
#             ref_lat2 = fields_target[4]
#             ref_lon3 = fields_target[5]
#             ref_lat3 = fields_target[6]
#
#             with open(IFG_list, "r") as ifg_file:
#                 for line_ifg in ifg_file:
#                     fields_ifg = line_ifg.split()
#                     PF_name = fields_ifg[1]
#                     dates = fields_ifg[2]
#                     IFG_name = PF_name + '.' + dates
#                     phs_file = RESULT_DIR + '/' + IFG_name + "_unwphs"
#
#                     ref_mean, r1, r2, r3 = read_phs_basedON_location(ref_lon1, ref_lat1, ref_lon2, ref_lat2, ref_lon3, ref_lat3, phs_file)
#
#                     result = open(out_file_name, 'a')
#                     result.write(str(TARGET_name) + ' ' + str(IFG_name) + ' ' + str(ref_mean) \
#                                  + ' ' + str(r1) + ' ' + str(r2) + ' ' + str(r3) + '\n')
#                     result.close()

if __name__ == '__main__':
    usage = "usage: %prog [options] shp raster_file"
    parser = OptionParser(usage=usage, version="1.0 2017-7-24")
    parser.description = 'Introduction:   '

    parser.add_option("-p", "--para",
                      action="store", dest="para_file",
                      help="the parameters file")

    (options, args) = parser.parse_args()
    #if len(sys.argv) < 2 or len(args) < 2:
    #    parser.print_help()
    #    sys.exit(2)
    # ## set parameters files
    # if options.para_file is None:
    #     print('error, no parameters file')
    #     parser.print_help()
    #     sys.exit(2)
    # else:
    #     parameters.set_saved_parafile_path(options.para_file)

    main(options, args)
