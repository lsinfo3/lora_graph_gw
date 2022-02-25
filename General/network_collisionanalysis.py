#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 25 21:07:31 2021

@author: frank
"""

try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass


import os
from glob import glob
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


#sensor data input
#inputpath = '../data/Replacement/2000mitFixedGateways/'
dirname = os.path.dirname(__file__)
inputpath = os.path.join(dirname, 'files')
sensor_files_hata = "sensors_transmissionrange*.json"
sensor_data_paths_hata = [file
                 for path, subdir, files in os.walk(inputpath)
                 for file in glob(os.path.join(path, sensor_files_hata))]
#sensor_data_paths_hata = [r"D:\DATA\Dokumente\Studium\Semester_7\Praktikum_LoRa\4Software\Graph_Metriken\Allgemeine_Dateien\Collision_Probability_Sim_Frank\files\sensors_transmissionrange_Placement.json"]
#%% 
#lora related parameters
payload_bytes = 16
cyclic_redundancy_check = 1
header_enabled = 1
header_length = 20
low_datarate_optimize = 0
coding_rate = 4
preamble_length = 8
sim_reruns = 100
sim_accuracy = 4 #number of after comma positions
simtime = 3600 #3600 equals to 1 msg per hour

messages_per_hour = 1
bandwidth = 125000
sf = [7, 8, 9, 10, 11, 12]
toa = np.zeros(len(sf))
for i in range(len(sf)):
    all_packet = (8 * payload_bytes - (4*sf[i]) + 8 + 16 * cyclic_redundancy_check + 20 * header_enabled) / (4 * sf[i] - 2*low_datarate_optimize)
    n_packet = 8 + np.max((np.ceil(all_packet)* (coding_rate + 4)), 0)
    total_symbols = preamble_length + 4.25 + n_packet
    symbol_duration = (2**sf[i])/bandwidth
    toa[i] = symbol_duration * total_symbols


collision_dataframe = pd.DataFrame({"path": sensor_data_paths_hata})

#%%
collision_probab_list = np.zeros(len(sensor_data_paths_hata))
all_collision_probabs = [[]] * len(sensor_data_paths_hata)
for i in range(len(sensor_data_paths_hata)):
    print('1B')
    print(i/len(sensor_data_paths_hata))
    sensor_data = pd.read_json(sensor_data_paths_hata[i])
    total_sensors_in_range = np.sum(sensor_data['NumberOfSensors'])
    tmp_collision_probab_list = np.zeros(sim_reruns)
    for k in range(sim_reruns):
        print(k/sim_reruns)
        current_sensor_counter = 0
        for j in range(len(sensor_data['lon'])):
            transmission_starts_this_entry = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['NumberOfSensors'][j]), sim_accuracy)
            transmission_starts_other_sensors = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['range'][j]), sim_accuracy)
            sf_collisions = sensor_data['sf_collisions'][j]
            for l in range(len(transmission_starts_this_entry)):
                print(sf_collisions)
                current_sensor_start = transmission_starts_this_entry[l]
                current_sensor_end = current_sensor_start + toa[sensor_data['SF'][j] - 7]
                toas_sensors_sf7 = np.zeros(sf_collisions[0]) + toa[0]
                toas_sensors_sf8 = np.zeros(sf_collisions[1]) + toa[1]
                toas_sensors_sf9 = np.zeros(sf_collisions[2]) + toa[2]
                toas_sensors_sf10 = np.zeros(sf_collisions[3]) + toa[3]
                toas_sensors_sf11 = np.zeros(sf_collisions[4]) + toa[4]
                toas_sensors_sf12 = np.zeros(sf_collisions[5]) + toa[5]
                
                toas_other_sensors = np.concatenate((toas_sensors_sf7, toas_sensors_sf8, toas_sensors_sf9, toas_sensors_sf10, toas_sensors_sf11, toas_sensors_sf12), axis=None)
                
                transmission_end_other_sensors = transmission_starts_other_sensors + toas_other_sensors
                
                other_sensors_df = pd.DataFrame({"start": transmission_starts_other_sensors, "end": transmission_end_other_sensors})
                other_sensors_df = other_sensors_df.sort_values('start')
                if len(np.where((other_sensors_df['start'] < current_sensor_start) & (other_sensors_df['end'] > current_sensor_start))[0]) > 0:
                    current_sensor_counter +=1
                elif len(np.where((other_sensors_df['start'] < current_sensor_end) & (other_sensors_df['end'] > current_sensor_end))[0]) > 0:
                    current_sensor_counter += 1
        
        tmp_collision_probab_list[k] = current_sensor_counter/total_sensors_in_range
    all_collision_probabs[i] = tmp_collision_probab_list
    collision_probab_list[i] = np.mean(tmp_collision_probab_list)
 
    
collision_dataframe['payload_1B'] = collision_probab_list 
collision_dataframe['payload_1B_list'] = all_collision_probabs


# payload_bytes = 4
# for i in range(len(sf)):
#     all_packet = (8 * payload_bytes - (4*sf[i]) + 8 + 16 * cyclic_redundancy_check + 20 * header_enabled) / (4 * sf[i] - 2*low_datarate_optimize)
#     n_packet = 8 + np.max((np.ceil(all_packet)* (coding_rate + 4)), 0)
#     total_symbols = preamble_length + 4.25 + n_packet
#     symbol_duration = (2**sf[i])/bandwidth
#     toa[i] = symbol_duration * total_symbols
    
# collision_probab_list = np.zeros(len(sensor_data_paths_hata))
# all_collision_probabs = [[]] * len(sensor_data_paths_hata)

# for i in range(len(sensor_data_paths_hata)):
#     print('4B')
#     print(i/len(sensor_data_paths_hata))
#     sensor_data = pd.read_json(sensor_data_paths_hata[i])
#     total_sensors_in_range = np.sum(sensor_data['NumberOfSensors'])
#     tmp_collision_probab_list = np.zeros(sim_reruns)
#     for k in range(sim_reruns):
#         print(k/sim_reruns)
        
#         current_sensor_counter = 0
#         for j in range(len(sensor_data['lon'])):
#             transmission_starts_this_entry = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['NumberOfSensors'][j]), sim_accuracy)
#             transmission_starts_other_sensors = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['range'][j]), sim_accuracy)
#             sf_collisions = sensor_data['sf_collisions'][j]
#             for l in range(len(transmission_starts_this_entry)):
#                 current_sensor_start = transmission_starts_this_entry[l]
#                 current_sensor_end = current_sensor_start + toa[sensor_data['SF'][j] - 7]
#                 toas_sensors_sf7 = np.zeros(sf_collisions[0]) + toa[0]
#                 toas_sensors_sf8 = np.zeros(sf_collisions[1]) + toa[1]
#                 toas_sensors_sf9 = np.zeros(sf_collisions[2]) + toa[2]
#                 toas_sensors_sf10 = np.zeros(sf_collisions[3]) + toa[3]
#                 toas_sensors_sf11 = np.zeros(sf_collisions[4]) + toa[4]
#                 toas_sensors_sf12 = np.zeros(sf_collisions[5]) + toa[5]
                
#                 toas_other_sensors = np.concatenate((toas_sensors_sf7, toas_sensors_sf8, toas_sensors_sf9, toas_sensors_sf10, toas_sensors_sf11, toas_sensors_sf12), axis=None)
                
#                 transmission_end_other_sensors = transmission_starts_other_sensors + toas_other_sensors
                
#                 other_sensors_df = pd.DataFrame({"start": transmission_starts_other_sensors, "end": transmission_end_other_sensors})
#                 other_sensors_df = other_sensors_df.sort_values('start')
#                 if len(np.where((other_sensors_df['start'] < current_sensor_start) & (other_sensors_df['end'] > current_sensor_start))[0]) > 0:
#                     current_sensor_counter +=1
#                 elif len(np.where((other_sensors_df['start'] < current_sensor_end) & (other_sensors_df['end'] > current_sensor_end))[0]) > 0:
#                     current_sensor_counter += 1
#         tmp_collision_probab_list[k] = current_sensor_counter/total_sensors_in_range
#     all_collision_probabs[i] = tmp_collision_probab_list
#     collision_probab_list[i] = np.mean(tmp_collision_probab_list)

# collision_dataframe['payload_4B'] = collision_probab_list
# collision_dataframe['payload_4B_list'] = all_collision_probabs

# payload_bytes = 8
# for i in range(len(sf)):
#     all_packet = (8 * payload_bytes - (4*sf[i]) + 8 + 16 * cyclic_redundancy_check + 20 * header_enabled) / (4 * sf[i] - 2*low_datarate_optimize)
#     n_packet = 8 + np.max((np.ceil(all_packet)* (coding_rate + 4)), 0)
#     total_symbols = preamble_length + 4.25 + n_packet
#     symbol_duration = (2**sf[i])/bandwidth
#     toa[i] = symbol_duration * total_symbols
    
# collision_probab_list = np.zeros(len(sensor_data_paths_hata))
# all_collision_probabs = [[]] * len(sensor_data_paths_hata)


# for i in range(len(sensor_data_paths_hata)):
#     print('8B')
#     print(i/len(sensor_data_paths_hata))
#     sensor_data = pd.read_json(sensor_data_paths_hata[i])
#     total_sensors_in_range = np.sum(sensor_data['NumberOfSensors'])
#     tmp_collision_probab_list = np.zeros(sim_reruns)
#     for k in range(sim_reruns):
#         print(k/sim_reruns)
        
#         current_sensor_counter = 0
#         for j in range(len(sensor_data['lon'])):
#             transmission_starts_this_entry = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['NumberOfSensors'][j]), sim_accuracy)
#             transmission_starts_other_sensors = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['range'][j]), sim_accuracy)
#             sf_collisions = sensor_data['sf_collisions'][j]
#             for l in range(len(transmission_starts_this_entry)):
#                 current_sensor_start = transmission_starts_this_entry[l]
#                 current_sensor_end = current_sensor_start + toa[sensor_data['SF'][j] - 7]
#                 toas_sensors_sf7 = np.zeros(sf_collisions[0]) + toa[0]
#                 toas_sensors_sf8 = np.zeros(sf_collisions[1]) + toa[1]
#                 toas_sensors_sf9 = np.zeros(sf_collisions[2]) + toa[2]
#                 toas_sensors_sf10 = np.zeros(sf_collisions[3]) + toa[3]
#                 toas_sensors_sf11 = np.zeros(sf_collisions[4]) + toa[4]
#                 toas_sensors_sf12 = np.zeros(sf_collisions[5]) + toa[5]
                
#                 toas_other_sensors = np.concatenate((toas_sensors_sf7, toas_sensors_sf8, toas_sensors_sf9, toas_sensors_sf10, toas_sensors_sf11, toas_sensors_sf12), axis=None)
                
#                 transmission_end_other_sensors = transmission_starts_other_sensors + toas_other_sensors
                
#                 other_sensors_df = pd.DataFrame({"start": transmission_starts_other_sensors, "end": transmission_end_other_sensors})
#                 other_sensors_df = other_sensors_df.sort_values('start')
#                 if len(np.where((other_sensors_df['start'] < current_sensor_start) & (other_sensors_df['end'] > current_sensor_start))[0]) > 0:
#                     current_sensor_counter +=1
#                 elif len(np.where((other_sensors_df['start'] < current_sensor_end) & (other_sensors_df['end'] > current_sensor_end))[0]) > 0:
#                     current_sensor_counter += 1
#         tmp_collision_probab_list[k] = current_sensor_counter/total_sensors_in_range
#     all_collision_probabs[i] = tmp_collision_probab_list
#     collision_probab_list[i] = np.mean(tmp_collision_probab_list)

# collision_dataframe['payload_8B'] = collision_probab_list
# collision_dataframe['payload_8B_list'] = all_collision_probabs


# payload_bytes = 16
# for i in range(len(sf)):
#     all_packet = (8 * payload_bytes - (4*sf[i]) + 8 + 16 * cyclic_redundancy_check + 20 * header_enabled) / (4 * sf[i] - 2*low_datarate_optimize)
#     n_packet = 8 + np.max((np.ceil(all_packet)* (coding_rate + 4)), 0)
#     total_symbols = preamble_length + 4.25 + n_packet
#     symbol_duration = (2**sf[i])/bandwidth
#     toa[i] = symbol_duration * total_symbols
    
# collision_probab_list = np.zeros(len(sensor_data_paths_hata))
# all_collision_probabs = [[]] * len(sensor_data_paths_hata)

# for i in range(len(sensor_data_paths_hata)):
#     print('16B')
#     print(i/len(sensor_data_paths_hata))
#     sensor_data = pd.read_json(sensor_data_paths_hata[i])
#     total_sensors_in_range = np.sum(sensor_data['NumberOfSensors'])
#     tmp_collision_probab_list = np.zeros(sim_reruns)
#     for k in range(sim_reruns):
#         print(k/sim_reruns)
#         current_sensor_counter = 0
#         for j in range(len(sensor_data['lon'])):
#             transmission_starts_this_entry = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['NumberOfSensors'][j]), sim_accuracy)
#             transmission_starts_other_sensors = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['range'][j]), sim_accuracy)
#             sf_collisions = sensor_data['sf_collisions'][j]
#             for l in range(len(transmission_starts_this_entry)):
#                 current_sensor_start = transmission_starts_this_entry[l]
#                 current_sensor_end = current_sensor_start + toa[sensor_data['SF'][j] - 7]
#                 toas_sensors_sf7 = np.zeros(sf_collisions[0]) + toa[0]
#                 toas_sensors_sf8 = np.zeros(sf_collisions[1]) + toa[1]
#                 toas_sensors_sf9 = np.zeros(sf_collisions[2]) + toa[2]
#                 toas_sensors_sf10 = np.zeros(sf_collisions[3]) + toa[3]
#                 toas_sensors_sf11 = np.zeros(sf_collisions[4]) + toa[4]
#                 toas_sensors_sf12 = np.zeros(sf_collisions[5]) + toa[5]
                
#                 toas_other_sensors = np.concatenate((toas_sensors_sf7, toas_sensors_sf8, toas_sensors_sf9, toas_sensors_sf10, toas_sensors_sf11, toas_sensors_sf12), axis=None)
                
#                 transmission_end_other_sensors = transmission_starts_other_sensors + toas_other_sensors
                
#                 other_sensors_df = pd.DataFrame({"start": transmission_starts_other_sensors, "end": transmission_end_other_sensors})
#                 other_sensors_df = other_sensors_df.sort_values('start')
#                 if len(np.where((other_sensors_df['start'] < current_sensor_start) & (other_sensors_df['end'] > current_sensor_start))[0]) > 0:
#                     current_sensor_counter +=1
#                 elif len(np.where((other_sensors_df['start'] < current_sensor_end) & (other_sensors_df['end'] > current_sensor_end))[0]) > 0:
#                     current_sensor_counter += 1
#         tmp_collision_probab_list[k] = current_sensor_counter/total_sensors_in_range
#     all_collision_probabs[i] = tmp_collision_probab_list
#     collision_probab_list[i] = np.mean(tmp_collision_probab_list)

# collision_dataframe['payload_16B'] = collision_probab_list
# collision_dataframe['payload_16B_list'] = all_collision_probabs


# payload_bytes = 32
# for i in range(len(sf)):
#     all_packet = (8 * payload_bytes - (4*sf[i]) + 8 + 16 * cyclic_redundancy_check + 20 * header_enabled) / (4 * sf[i] - 2*low_datarate_optimize)
#     n_packet = 8 + np.max((np.ceil(all_packet)* (coding_rate + 4)), 0)
#     total_symbols = preamble_length + 4.25 + n_packet
#     symbol_duration = (2**sf[i])/bandwidth
#     toa[i] = symbol_duration * total_symbols
    
# collision_probab_list = np.zeros(len(sensor_data_paths_hata))
# all_collision_probabs = [[]] * len(sensor_data_paths_hata)

# for i in range(len(sensor_data_paths_hata)):
#     print('32B')
#     print(i/len(sensor_data_paths_hata))
#     sensor_data = pd.read_json(sensor_data_paths_hata[i])
#     total_sensors_in_range = np.sum(sensor_data['NumberOfSensors'])
#     tmp_collision_probab_list = np.zeros(sim_reruns)
#     for k in range(sim_reruns):
#         print(k/sim_reruns)
#         current_sensor_counter = 0
#         for j in range(len(sensor_data['lon'])):
#             transmission_starts_this_entry = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['NumberOfSensors'][j]), sim_accuracy)
#             transmission_starts_other_sensors = np.round(np.random.uniform(low = 0, high=3600, size=sensor_data['range'][j]), sim_accuracy)
#             sf_collisions = sensor_data['sf_collisions'][j]
#             for l in range(len(transmission_starts_this_entry)):
#                 current_sensor_start = transmission_starts_this_entry[l]
#                 current_sensor_end = current_sensor_start + toa[sensor_data['SF'][j] - 7]
#                 toas_sensors_sf7 = np.zeros(sf_collisions[0]) + toa[0]
#                 toas_sensors_sf8 = np.zeros(sf_collisions[1]) + toa[1]
#                 toas_sensors_sf9 = np.zeros(sf_collisions[2]) + toa[2]
#                 toas_sensors_sf10 = np.zeros(sf_collisions[3]) + toa[3]
#                 toas_sensors_sf11 = np.zeros(sf_collisions[4]) + toa[4]
#                 toas_sensors_sf12 = np.zeros(sf_collisions[5]) + toa[5]
                
#                 toas_other_sensors = np.concatenate((toas_sensors_sf7, toas_sensors_sf8, toas_sensors_sf9, toas_sensors_sf10, toas_sensors_sf11, toas_sensors_sf12), axis=None)
                
#                 transmission_end_other_sensors = transmission_starts_other_sensors + toas_other_sensors
                
#                 other_sensors_df = pd.DataFrame({"start": transmission_starts_other_sensors, "end": transmission_end_other_sensors})
#                 other_sensors_df = other_sensors_df.sort_values('start')
#                 if len(np.where((other_sensors_df['start'] < current_sensor_start) & (other_sensors_df['end'] > current_sensor_start))[0]) > 0:
#                     current_sensor_counter +=1
#                 elif len(np.where((other_sensors_df['start'] < current_sensor_end) & (other_sensors_df['end'] > current_sensor_end))[0]) > 0:
#                     current_sensor_counter += 1
#         tmp_collision_probab_list[k] = current_sensor_counter/total_sensors_in_range
#     all_collision_probabs[i] = tmp_collision_probab_list
#     collision_probab_list[i] = np.mean(tmp_collision_probab_list)

# collision_dataframe['payload_32B'] = collision_probab_list
# collision_dataframe['payload_32B_list'] = all_collision_probabs

collision_dataframe.to_csv('2000mitFixedGateways.csv')
collision_dataframe.to_json('2000mitFixedGateways.json')
