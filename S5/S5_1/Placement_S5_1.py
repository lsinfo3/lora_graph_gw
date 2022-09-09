import math
import itertools
import csv
import utm
from datetime import datetime
import pandas as pd
from multiprocessing import Pool
from sklearn.cluster import KMeans
import numpy as np

def calculateDistance(x1,x2,y1,y2):
    return math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))

def generateEdges(nodes,Max_Range,Max_Sensors):
    edges=[[]for i in nodes]
    previous_covered=0
    for curr_sensor in nodes:
        if(int((nodes.index(curr_sensor)/len(nodes)*100))>previous_covered):
            print("Placement: "+str(int((nodes.index(curr_sensor)/len(nodes)*100))))
            previous_covered+=1
        curr_connected=0
        for sensor_to_test in nodes:
            if(sensor_to_test!=curr_sensor):
                if(calculateDistance(curr_sensor[0],sensor_to_test[0],curr_sensor[1],sensor_to_test[1])<=Max_Range and curr_connected<Max_Sensors):
                    edges[nodes.index(curr_sensor)].append(nodes.index(sensor_to_test))
                    curr_connected+=1
    return(edges)

def hata(sf,gw_height,sens_height):#returns distance in m
    # represents Spreading Factor Tolerances for Path Loss in dB
    plrange = [131, 134, 137, 140, 141, 144]
    distance = 10**(-(69.55+76.872985-13.82*math.log10(gw_height)-3.2*(math.log10(
        11.75*sens_height)**2)+4.97-plrange[sf-7])/(44.9-6.55*math.log10(gw_height)))
    return distance*1000

def create_placement(vars):
    Max_Range=vars[0]
    Sensors=vars[1]
    cluster_index=vars[2]
    print(Max_Range)
    start=datetime.now()
    #Sensors=[[7,10],[10,6],[11,7],[11,12],[16,2]] #blue set
    Gateways=[]
    #Max_Range=hata(12,15,1)
    #Max_Gateways=10
    Min_Sensors=0
    Max_Sensors=1000
    Target_Coverage=100#%
    oldsensors=[i for i in Sensors]
    #for curr in range(Max_Gateways):
    while(100-(len(oldsensors)/len(Sensors))*100<Target_Coverage):
        edges=generateEdges(oldsensors,Max_Range,Max_Sensors)
        if(len(edges)<1):
            break
        designatedgw=max(edges,key=len)
        if(len(designatedgw)<Min_Sensors):
            break
        Gateways.append(Sensors.index(oldsensors[edges.index(designatedgw)]))
        #print(Gateways)
        newsensors=[]
        for curr_sensor in oldsensors:   
            if(oldsensors.index(curr_sensor)!=edges.index(designatedgw) and oldsensors.index(curr_sensor) not in designatedgw):
                newsensors.append(curr_sensor)
        oldsensors=newsensors
        #print((len(oldsensors)/len(Sensors)))
    #print(datetime.now()-start)
    output = {"id": [], "x": [], "y": [], "height": [],"environment": []}
    for g in Gateways:
        latlon=utm.to_latlon(Sensors[g][0],Sensors[g][1],32,"U")
        output['id'].append(g)
        output['x'].append(latlon[1])
        output['y'].append(latlon[0])
        output['height'].append(5.0)
        output['environment'].append("urban")
        #print(Sensors[g])
    #pd.DataFrame(data=output).to_csv('gateways_Placement_Cluster'+str(int(cluster_index))+'.csv')
    #print("generating matching SF and bestGW")
    Sensors_to_export=[[Sensors[i][0],Sensors[i][1],0,0] for i in range(len(Sensors))]
    edgesSFs=[generateEdges(Sensors,hata(i,15,1),Max_Sensors) for i in range(7,13)]
    for sf in range(12,6,-1):
        #print(sf)
        for g in Gateways:
            for sens in edgesSFs[sf-7][g]:
                Sensors_to_export[sens][2]=sf
                Sensors_to_export[sens][3]=g
    #print(Sensors_to_export)
    outputsens = {"lon": [], "lat": [], "BestGW": [],"SF": [], "NumberOfSensors": []}
    for sens in Sensors_to_export:
        if(sens[2]!=0):
            latlon=utm.to_latlon(sens[0],sens[1],32,"U")
            outputsens['lat'].append(latlon[1])
            outputsens['lon'].append(latlon[0])
            outputsens['BestGW'].append(sens[3])
            outputsens['SF'].append(sens[2])
            outputsens['NumberOfSensors'].append(1)
    #print(output)
    #pd.DataFrame(data=output).to_csv('reachable_sensors_Cluster'+str(int(cluster_index))+'.csv')
    #pd.DataFrame(data=output).to_json('reachable_sensors_Cluster'+str(int(cluster_index))+'.json')
    return([output,outputsens])

def run_clustering(num_clusters,num_threads,run):
    base_range=hata(12,15,1)
    Sensors=[]
    #num_clusters=2
    #num_threads=2 #only values smaller than or equal to num_clusters improve compute time
    with open("sensors.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append([float(curr[0]),float(curr[1])])
            except:
                pass
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(Sensors)
    clusters = kmeans.predict(Sensors)
    partial_sensors=[[] for i in range(num_clusters)]
    for location in range(len(Sensors)):
        partial_sensors[clusters[location]].append(Sensors[location])
    with Pool(num_clusters) as p:
        devices_against_collision = p.map(create_placement, [[base_range,partial_sensors[i],i] for i in range(num_clusters)])
    output={"id": [], "x": [], "y": [], "height": [],"environment": []}
    outputsens={"lon": [], "lat": [], "BestGW": [],"SF": [], "NumberOfSensors": []}
    currgw_index=0
    for curroutput in devices_against_collision:
        for i in range(len(curroutput[0]['id'])):
            output['id'].append(currgw_index)
            output['x'].append(curroutput[0]['x'][i])
            output['y'].append(curroutput[0]['y'][i])
            output['height'].append(curroutput[0]['height'][i])
            output['environment'].append(curroutput[0]['environment'][i])
            currgw_index+=1
        for i in range(len(curroutput[1]['lon'])):
            outputsens['lat'].append(curroutput[1]['lat'][i])
            outputsens['lon'].append(curroutput[1]['lon'][i])
            outputsens['BestGW'].append(curroutput[1]['BestGW'][i])
            outputsens['SF'].append(curroutput[1]['SF'][i])
            outputsens['NumberOfSensors'].append(curroutput[1]['NumberOfSensors'][i])
    pd.DataFrame(data=output).to_csv('gateways_Placement_Cluster_'+str(num_clusters)+'_run_'+str(run)+'.csv')
    pd.DataFrame(data=outputsens).to_csv('reachable_sensors_Cluster_'+str(num_clusters)+'_run_'+str(run)+'.csv')
    pd.DataFrame(data=outputsens).to_json('reachable_sensors_Cluster_'+str(num_clusters)+'_run_'+str(run)+'.json')

if __name__ == "__main__":
    num_threads=14
    configurations=[2,4,6,8,10,12,14,16,18,20,24,28,32,36,40]
    output={"configurations": [], "runtimes": []}
    for run in range(10):
        for i in configurations:
            start=datetime.now()
            run_clustering(i,min(num_threads,i),run)
            output["runtimes"].append(str(datetime.now()-start))
            output["configurations"].append(i)
            #print(output)
            df=pd.DataFrame.from_dict(output)
            df.to_csv("runtimes.csv",index=False,header=True)
