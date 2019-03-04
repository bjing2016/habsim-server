import numpy as np
import pygrib
import urllib.request
import os.path
import sys
from datetime import datetime, timedelta



levels = [10, 20, 30, 50, 70,\
          100, 150, 200, 250, 300, 350, 400, 450,\
          500, 550, 600, 650, 700, 750, 800, 850,\
          900, 925, 950, 975, 1000]

def complete_run(y, m, d, h, path):

    for t in range(0, 384+6, 6):
        for n in range(1, 21):
            single_run(y,m,d,h,t,n, path)

def single_run(y,m,d,h,t,n, path):
    

    
    url = "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.{}{}{}/{}/pgrb2/gep{}.t{}z.pgrb2f{}"\
        .format(y, str(m).zfill(2), str(d).zfill(2), str(h).zfill(2), str(n).zfill(2), str(h).zfill(2), str(t).zfill(2))
    print(url)
    ## url = "ftp://ftp.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20190302/00/pgrb2/gep01.t00z.pgrb2f12"
    base = datetime(y, m, d, h)
    basestring = base.strftime("%Y%m%d%H")    
    pred = base + timedelta(hours=t)

    predstring = pred.strftime("%Y%m%d%H")
    savename = basestring + "_" + predstring + "_" + str(n).zfill(2)

    if os.path.exists(path+'/'+savename+".npy"):
        return

    print("Downloading " + savename)

    urllib.request.urlretrieve (url, path + "/" + savename + ".grb2")
            
    print("Unpacking " + savename)

    data = grb2_to_array(path + "/" + savename)

    print("Saving " + savename)

    np.save(path + "/" + savename + ".npy", data)
    print("Deleting " + savename)

    os.remove(path + "/" + savename + ".grb2")



def grb2_to_array(filename): 
    ## Array format: array[u,v][Pressure][Lat][Lon] ##
    ## Currently [lat 90 to -90][lon 0 to 359]
    grbs = pygrib.open(filename + ".grb2")
    
    
    dataset = np.zeros((2, len(levels), 181, 360))

    ### Thanks to KMarshland for pointers on using PyGrib ###
    for i in range(len(levels)):
        ### [lat, lat, lon, lon]
        for grb in grbs.select(shortName='u',typeOfLevel='isobaricInhPa', level = levels[i]):
            dataset[0][i] = grb.data()[0]

    for i in range(len(levels)):
        for grb in grbs.select(shortName='v',typeOfLevel='isobaricInhPa', level = levels[i]):
            dataset[1][i] = grb.data()[0]

    return dataset



year, month, day, hour = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])

complete_run(year, month, day, hour, "../gefs")
