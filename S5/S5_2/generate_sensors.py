import utm
import numpy as np
import pandas as pd
import math

def uniform(bb,amount):
    coords=[]
    ysteps=np.linspace(bb[2],bb[3],dtype=float,num=int(math.sqrt(amount)))
    for y in ysteps:
        xsteps=np.linspace(bb[0],bb[1],dtype=float,num=int(math.sqrt(amount)))
        for x in xsteps:
            coords.append([x,y])
    return coords

def random_square(bb,amount):
    return([[(np.random.rand()*(bb[1]-bb[0]))+bb[0],(np.random.rand()*(bb[3]-bb[2]))+bb[2]] for i in range(amount)])

def wrong_circle(bb,amount):
    coords=[]
    for i in range(amount):
        r=math.sqrt(np.random.rand())
        u=np.random.rand()*2*math.pi
        x=((r*math.cos(u)+1)*0.5)
        y=((r*math.sin(u)+1)*0.5)
        coords.append([x*(bb[1]-bb[0])+bb[0],(y*(bb[3]-bb[2]))+bb[2]])
    return(coords)

def circle(bb,amount):
    coords=[]
    for i in range(amount):
        r=np.random.rand()
        u=np.random.rand()*2*math.pi
        x=((r*math.cos(u)+1)*0.5)
        y=((r*math.sin(u)+1)*0.5)
        coords.append([x*(bb[1]-bb[0])+bb[0],(y*(bb[3]-bb[2]))+bb[2]])
    return(coords)

def export(coords,filename):
    output={"x": [], "y": []}
    for i in coords:
        output["x"].append(i[0])
        output["y"].append(i[1])
        #print(output)
    df=pd.DataFrame.from_dict(output)
    df.to_csv(filename,index=False,header=False)

if __name__ == "__main__":
    bb1=utm.from_latlon(49.88548855727779,9.768027390254648)
    bb2=utm.from_latlon(49.895504572874735,10.095992860921562)
    bb3=utm.from_latlon(49.70156986612576,10.112012787654349)
    bb4=utm.from_latlon(49.69652851334897,9.78352020241069)
    bb=[bb1,bb2,bb3,bb4]
    minx=float('inf')
    miny=float('inf')
    maxx=0
    maxy=0
    for curr in bb:
        if(curr[0]<minx):
            minx=curr[0]
        if(curr[1]<miny):
            miny=curr[1]
        if(curr[0]>maxx):
            maxx=curr[0]
        if(curr[1]>maxy):
            maxy=curr[1]
    bb=[minx,maxx,miny,maxy]
    for i in range(10):
        export(wrong_circle(bb,5000),'sensors_wrong_circle_'+str(i)+'.csv')
        export(circle(bb,5000),'sensors_circle_'+str(i)+'.csv')
        export(random_square(bb,5000),'sensors_random_square_'+str(i)+'.csv')
    export(uniform(bb,5000),'sensors_uniform.csv')