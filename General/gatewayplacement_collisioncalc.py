#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 14:45:57 2021

@author: frank
"""
try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass


import os
import math
from glob import glob
import pandas as pd
import time

import numpy as np

from numpy import arccos, dot, pi, cross
from numpy.linalg import  norm

import utm

pd.options.mode.chained_assignment=None

def distance_numpy(A, B, P):
    """ segment line AB, point P, where each one is an array([x, y]) """
    if all(A == P) or all(B == P):
        return 0
    if arccos(dot((P - A) / norm(P - A), (B - A) / norm(B - A))) > pi / 2:
        return norm(P - A)
    if arccos(dot((P - B) / norm(P - B), (A - B) / norm(A - B))) > pi / 2:
        return norm(P - B)
    return norm(cross(A-B, A-P))/norm(B-A)


def hata(gw_height, gw_environment, sf):
    try:
        sens_height = 1
        # represents Spreading Factor Tolerances for Path Loss in dB
        plrange = [131, 134, 137, 140, 141, 144]
        distance = 10**(-(69.55+76.872985-13.82*math.log10(gw_height)-3.2*(math.log10(
            11.54*sens_height)**2)-4.97-plrange[sf-7])/(44.9-6.55*math.log10(gw_height)))
        distance = distance*1000
    except:
        distance = 10
    return distance


def cost231(gw_height, gw_environment, sf):
    try:
        sens_height = 1
        c_m = 0
        a_h = 3.2*(math.log10(11.75*sens_height))**2 - 4.79
        if(gw_environment == "urban"):
            pass
        elif(gw_environment == "suburban"):
            c_m = 3
            a_h = (1.1*math.log10(868.1)-0.7) * \
                sens_height-(1.5*math.log10(868.1)-0.8)
        elif(gw_environment == "rural"):
            c_m = 3
            a_h = (1.1*math.log10(868.1)-0.7) * \
                sens_height-(1.5*math.log10(868.1)-0.8)
        # represents Spreading Factor Tolerances for Path Loss in dB
        plrange = [131, 134, 137, 140, 141, 144]
        distance = 10**((46.3+33.9*math.log10(868.1)-13.82*math.log10(gw_height) -
                          a_h-plrange[sf-7]+c_m)/-(44.9-6.55*math.log10(gw_height)))
        distance = distance*1000
    except:
        distance = 10
    return distance


def lee(gw_height, gw_environment, sf):
    try:
        sens_height = 1
        # represents Spreading Factor Tolerances for Path Loss in dB
        plrange = [131, 134, 137, 140, 141, 144]
        L_0_opt = [89, 101.7, 110]
        g_opt = [43.5, 38.5, 36.8]
        L_0 = 0
        g = 0
        F_1 = (gw_height/30.48)**2
        F_2 = (1/2)
        if(sens_height > 3):
            F_3 = (sens_height/3)**2
        else:
            F_3 = (sens_height/3)
        F_4 = (868.1/900)**(-2.5)
        F_5 = 2
        if(gw_environment == "urban"):
            L_0 = L_0_opt[2]
            g = g_opt[2]
        elif(gw_environment == "suburban"):
            L_0 = L_0_opt[1]
            g = g_opt[1]
        elif(gw_environment == "rural"):
            L_0 = L_0_opt[0]
            g = g_opt[0]
        F_0 = F_1*F_2*F_3*F_4*F_5
        distance = 10**((L_0-plrange[sf-7]-10*math.log10(F_0))/(-g))
        distance = distance*1000
    except:
        distance = 10
    return distance
#%%


pd.options.display.float_format = '{:.2f}'.format

#inputpath = '../data/to_process/Randomness_tests/RandomnessOfInput/gw_05/'

#inputpath = r"D:\DATA\Dokumente\Studium\Semester_7\Praktikum_LoRa\4Software\1Evaluated\Collision_Probability_Sim_Frank\files"
dirname = os.path.dirname(__file__)
inputpath = os.path.join(dirname, 'files')

sensor_files = "reachable_sensors*.json"
gateway_files = "gateways*.csv"
#%%
sensor_data_paths = [file
                 for path, subdir, files in os.walk(os.path.normpath(inputpath))
                 for file in glob(os.path.join(path, sensor_files))]
gateway_data_paths = [file
                 for path, subdir, files in os.walk(os.path.normpath(inputpath))
                 for file in glob(os.path.join(path, gateway_files))]

#sensor_data_paths = sorted(sensor_data_paths)
#gateway_data_paths = sorted(gateway_data_paths)
#sensor_data_paths=[r"D:\DATA\Dokumente\Studium\Semester_7\Praktikum_LoRa\4Software\Graph_Metriken\Allgemeine_Dateien\Collision_Probability_Sim_Frank\files\reachable_sensors_Placement.json"]
#gateway_data_paths=[r"D:\DATA\Dokumente\Studium\Semester_7\Praktikum_LoRa\4Software\Graph_Metriken\Allgemeine_Dateien\Collision_Probability_Sim_Frank\files\gateways_Placement.csv"]
print(sensor_data_paths)

gateway_height = 5.0 #pd.unique(gateway_data['height'])[0]
gateway_env = 'urban' #pd.unique(gateway_data['environment'])[0]

sf = [7,8,9,10,11,12]
#lee_distances = np.zeros(len(sf))
#cost_distances = np.zeros(len(sf))
hata_distances = np.zeros(len(sf))

#get transmission distances by model
for i in range(len(sf)):
    #lee_distances[i] = lee(gateway_height, gateway_env, sf[i])
    #cost_distances[i] = cost231(gateway_height, gateway_env, sf[i])
    hata_distances[i] = hata(gateway_height, gateway_env, sf[i])

    gateway_data_paths = sorted(gateway_data_paths)
    sensor_data_paths = sorted(sensor_data_paths)
#%%
for i in range(len(sensor_data_paths)):
    gateway_data = pd.read_csv(gateway_data_paths[i], sep=r'\s*,\s*',
                           header=0, encoding='ascii', engine='python')
        
    print("allrun" + str(i/len(sensor_data_paths)))
    
    sensor_data = pd.read_json(sensor_data_paths[i])
    sensor_data['distance'] = np.zeros(len(sensor_data))      
    sensor_data['range'] = np.zeros(len(sensor_data))      
    sensor_data['sf_collisions'] = np.empty((len(sensor_data), 0)).tolist()
    sensor_data['gw_x'] = np.zeros(len(sensor_data)) 
    sensor_data['gw_y'] = np.zeros(len(sensor_data)) 
    sensor_data['sen_x'] = np.zeros(len(sensor_data)) 
    sensor_data['sen_y'] = np.zeros(len(sensor_data)) 
    
    gateway_data['gw_lat_y'] = np.zeros(len(gateway_data))
    gateway_data['gw_lon_x'] = np.zeros(len(gateway_data))

    for j in range(len(gateway_data)):
        tmp = utm.from_latlon(gateway_data['y'][j], gateway_data['x'][j])
        gateway_data["gw_lat_y"][j] = tmp[0]
        gateway_data["gw_lon_x"][j] = tmp[1]
        
        curr_id = gateway_data["id"][j]
        
        gw_ids = np.where(sensor_data['BestGW'] == curr_id)
        sensor_data.loc[list(gw_ids[0]), 'gw_y'] =  gateway_data['gw_lat_y'][j] 
        sensor_data.loc[list(gw_ids[0]), 'gw_x'] =  gateway_data['gw_lon_x'][j] 
    
    if np.min(sensor_data['gw_x']) == 0:
        print(gateway_data_paths[i])
        print(sensor_data_paths[i])
    if np.min(sensor_data['gw_y']) == 0:
        print(gateway_data_paths[i])
        print(sensor_data_paths[i])

    #if "hata" in sensor_data_paths[i]:
    if(True):         
        for j in range(len(sensor_data)):
            sensor_data['sf_collisions'][j] = [0,0,0,0,0,0]
            sensor_data['distance'][j] = hata_distances[sensor_data['SF'][j]-7]
                                  
            tmp = utm.from_latlon(sensor_data['lat'][j], sensor_data['lon'][j])
            sensor_data["sen_y"][j] = tmp[0]
            sensor_data["sen_x"][j] = tmp[1]
            
        for j in range(len(sensor_data)):
            if(sensor_data['NumberOfSensors'][j] >= 1):
                sensor_data['range'][j] += sensor_data['NumberOfSensors'][j]
                sensor_data['sf_collisions'][j][sensor_data['SF'][j]-7] += sensor_data['NumberOfSensors'][j]
            #print("thisrun" + str(j/len(sensor_data)))
            
            for l in range(j+1, len(sensor_data)):
                if(l != j):
                    p1 = (sensor_data.sen_x[j], sensor_data.sen_y[j])
                    p1 = np.asarray(p1)
                    p2 = (sensor_data.gw_x[j], sensor_data.gw_y[j])
                    p2 = np.asarray(p2)
                    p3 = (sensor_data.sen_x[l], sensor_data.sen_y[l])
                    p3 = np.asarray(p3)
                    
                    dist = distance_numpy(p1,p2,p3)
                    
                    sensor_dist = math.hypot(sensor_data.sen_x[j] - sensor_data.sen_x[l], sensor_data.sen_y[j] - sensor_data.sen_y[l])
                    
                    if(sensor_dist < sensor_data['distance'][l]):
                        sensor_data['range'][j] +=  sensor_data['NumberOfSensors'][l]
                        sensor_data['sf_collisions'][j][sensor_data['SF'][l]-7] += sensor_data['NumberOfSensors'][l]
                    elif(dist < sensor_data['distance'][l]):
                        sensor_data['range'][j] +=  sensor_data['NumberOfSensors'][l]
                        sensor_data['sf_collisions'][j][sensor_data['SF'][l]-7] += sensor_data['NumberOfSensors'][l]

    outputPath = sensor_data_paths[i].replace('reachable_sensors', 'sensors_transmissionrange')
    sensor_data.to_json(outputPath)
    print(sensor_data)
   
    
# =============================================================================
#     if "lee" in sensor_data_paths[i]: 
#         for j in range(len(sensor_data)):
#             sensor_data['sf_collisions'][j] = [0,0,0,0,0,0]           
#             sensor_data['distance'][j] = lee_distances[sensor_data['SF'][j]-7]
#             
#             tmp = utm.from_latlon(sensor_data['lat'][j], sensor_data['lon'][j])
#             sensor_data["sen_y"][j] = tmp[0]
#             sensor_data["sen_x"][j] = tmp[1]
#             
#         for j in range(len(sensor_data)):
#             if(sensor_data['NumberOfSensors'][j] > 1):
#                 sensor_data['range'][j] += sensor_data['NumberOfSensors'][j]-1
#                 sensor_data['sf_collisions'][j][sensor_data['SF'][j]-7] += sensor_data['NumberOfSensors'][j]-1
#       
#             #print("thisrun" + str(j/len(sensor_data)))
#             for l in range(j+1, len(sensor_data)):
#                 if(l != j):
#                     p1 = (sensor_data.sen_x[j], sensor_data.sen_y[j])
#                     p1 = np.asarray(p1)
#                     p2 = (sensor_data.gw_x[j], sensor_data.gw_y[j])
#                     p2 = np.asarray(p2)
#                     p3 = (sensor_data.sen_x[l], sensor_data.sen_y[l])
#                     p3 = np.asarray(p3)
#                     
#                     dist = distance_numpy(p1,p2,p3)
#                     
#                     sensor_dist = math.hypot(sensor_data.sen_x[j] - sensor_data.sen_x[l], sensor_data.sen_y[j] - sensor_data.sen_y[l])
#               
#                     if(sensor_dist < sensor_data['distance'][l]):
#                         sensor_data['range'][j] +=  sensor_data['NumberOfSensors'][l]
#                         sensor_data['sf_collisions'][j][sensor_data['SF'][l]-7] += sensor_data['NumberOfSensors'][l]
#                     elif(dist < sensor_data['distance'][l]):
#                         sensor_data['range'][j] +=  sensor_data['NumberOfSensors'][l]
#                         sensor_data['sf_collisions'][j][sensor_data['SF'][l]-7] += sensor_data['NumberOfSensors'][l]
# 
# =============================================================================
    
# =============================================================================
#     if "cost" in sensor_data_paths[i]:        
#         for j in range(len(sensor_data)):
#             
#             sensor_data['sf_collisions'][j] = [0,0,0,0,0,0]
#             sensor_data['distance'][j] = cost_distances[sensor_data['SF'][j]-7]
#             
#             tmp = utm.from_latlon(sensor_data['lat'][j], sensor_data['lon'][j])
#             sensor_data["sen_y"][j] = tmp[0]
#             sensor_data["sen_x"][j] = tmp[1]
#             
#         for j in range(len(sensor_data)):
#             if(sensor_data['NumberOfSensors'][j] > 1):
#                 sensor_data['range'][j] += sensor_data['NumberOfSensors'][j]-1
#                 sensor_data['sf_collisions'][j][sensor_data['SF'][j]-7] += sensor_data['NumberOfSensors'][j]-1
#       
#             #print("thisrun" + str(j/len(sensor_data)))
#             for l in range(0, len(sensor_data)):
#                 if(l != j):
#                     p1 = (sensor_data.sen_x[j], sensor_data.sen_y[j])
#                     p1 = np.asarray(p1)
#                     p2 = (sensor_data.gw_x[j], sensor_data.gw_y[j])
#                     p2 = np.asarray(p2)
#                     p3 = (sensor_data.sen_x[l], sensor_data.sen_y[l])
#                     p3 = np.asarray(p3)
#                     
#                     dist = distance_numpy(p1,p2,p3)
#                     
#                     sensor_dist = math.hypot(sensor_data.sen_x[j] - sensor_data.sen_x[l], sensor_data.sen_y[j] - sensor_data.sen_y[l])
#                     
#                     if(sensor_dist < sensor_data['distance'][l]):
#                         sensor_data['range'][j] +=  sensor_data['NumberOfSensors'][l]
#                         sensor_data['sf_collisions'][j][sensor_data['SF'][l]-7] += sensor_data['NumberOfSensors'][l]
#                     elif(dist < sensor_data['distance'][l]):
#                         sensor_data['range'][j] +=  sensor_data['NumberOfSensors'][l]
#                         sensor_data['sf_collisions'][j][sensor_data['SF'][l]-7] += sensor_data['NumberOfSensors'][l]
# 
# =============================================================================


