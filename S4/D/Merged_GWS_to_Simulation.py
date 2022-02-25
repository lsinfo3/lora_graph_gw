import math
import itertools
import csv
import utm
from datetime import datetime
import pandas as pd
from multiprocessing import Pool

def calculateDistance(x1,x2,y1,y2):
    return math.sqrt(math.pow(x1-x2,2)+math.pow(y1-y2,2))


def generateEdges(nodes,Max_Range,Max_Sensors):
    edges=[[]for i in nodes]
    previous_covered=0
    for curr_sensor in nodes:
        if(int((nodes.index(curr_sensor)/len(nodes)*100))>previous_covered):
            print("Placement: "+str(int((nodes.index(curr_sensor)/len(nodes)*100))))
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
    Sensors=vars[0]
    Gateways=vars[1]
    Max_Sensors=vars[2]
    output = {"id": [], "x": [], "y": [], "height": [],"environment": []}
    for g in Gateways:
        latlon=utm.from_latlon(g[0],g[1])
        output['id'].append(Gateways.index(g))
        output['x'].append(g[0])
        output['y'].append(g[1])
        output['height'].append(5.0)
        output['environment'].append("urban")
        #print(Sensors[g])
    pd.DataFrame(data=output).to_csv('gateways_Placement_San_Francisco_Voronoi.csv')
    NewGWIndex=[]
    for g in Gateways:
        latlon=utm.from_latlon(g[1],g[0])
        print(utm.from_latlon(g[1],g[0]))
        print([latlon[0],latlon[1]])
        Sensors.append([latlon[0],latlon[1]])
        NewGWIndex.append(Sensors.index([latlon[0],latlon[1]]))
    #print("generating matching SF and bestGW")
    Sensors_to_export=[[Sensors[i][0],Sensors[i][1],0,0,float("Inf"),0] for i in range(len(Sensors))]
    #edgesSFs=[generateEdges(Sensors,hata(i,15,1),Max_Sensors) for i in range(7,13)]
    print(NewGWIndex)
    for sens in Sensors_to_export:
        for g in NewGWIndex:
            dist=calculateDistance(Sensors[g][0],sens[0],Sensors[g][1],sens[1])
            if(dist<sens[4]):
                sens[4]=dist
                sens[3]=NewGWIndex.index(g)
                currsf=12
                for sf in range(12,6,-1):
                    if dist<hata(sf,15,1):
                        currsf=sf
                sens[2]=currsf
                sens[5]+=1
    #for sf in range(12,6,-1):
        #print(sf)
    #    for g in Gateways:
    #        for sens in edgesSFs[sf-7][g]:
    #            Sensors_to_export[sens][2]=sf
    #            Sensors_to_export[sens][3]=g
    #print(Sensors_to_export)
    output = {"lon": [], "lat": [], "BestGW": [],"SF": [], "NumberOfSensors": [],"NumGWs":[]}
    for sens in Sensors_to_export:
        if(sens[2]!=0 and Sensors_to_export.index(sens) not in NewGWIndex):
            latlon=utm.to_latlon(sens[0],sens[1],32,"U")
            output['lat'].append(latlon[1])
            output['lon'].append(latlon[0])
            output['BestGW'].append(sens[3])
            output['SF'].append(sens[2])
            output['NumberOfSensors'].append(1)
            output['NumGWs'].append(sens[5])
    #print(output)
    pd.DataFrame(data=output).to_csv('reachable_sensors_San_Francisco_Voronoi.csv')
    pd.DataFrame(data=output).to_json('reachable_sensors_San_Francisco_Voronoi.json')


if __name__ == "__main__":
    Max_Sensors=750
    Sensors=[]
    Gateways=[]
    with open("sensors.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append([float(curr[0]),float(curr[1])])
            except:
                pass
    with open("gateways.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Gateways.append([float(curr[2]),float(curr[3])])
            except:
                pass

        create_placement([Sensors,Gateways,Max_Sensors])
