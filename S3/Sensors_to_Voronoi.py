import csv
import pandas as pd

if __name__ == "__main__":
    Sensors=[]
    with open("sensors.csv", newline='') as csvfile:
        data = list(csv.reader(csvfile))
        for curr in data:
            try:
                Sensors.append([float(curr[0]),float(curr[1])])
            except:
                pass
    output=[]
    output.append([len(Sensors),750.0])
    for i in Sensors:
        output.append(i)
    output.append([len(Sensors)])
    for i in Sensors:
        output.append(i)
    with open('input.txt', 'w',newline='') as f:
        write = csv.writer(f) 
        write.writerows(output)