import pandas as pd
import numpy as np
import os
import utm
from datetime import timedelta
from .. import read


def release(path):
    fin = open(os.path.join(path, 'input.Ptrac'), 'r')
    s = fin.readline()
    while 'release year' not in s:
        s = fin.readline()
    yr = int(s.split(',')[0])
    s = fin.readline()
    mth = int(s.split(',')[0])
    s = fin.readline()
    day = int(s.split(',')[0])
    print('Release Date: {}-{}-{}'.format(yr, mth, day))
    return yr, mth, day


def particles(path):
    yr, mth, day = release(path)

    coords = read.coords(os.path.join(path, 'input'), 14, 'utm')
    xMin = coords.easting.min()
    yMin = coords.northing.min()
    print('xmin = {}\nymin = {}'.format(xMin, yMin))

    fils = ['particles1.w', 'particles2.w', 'particles3.w', 'particles4.w',
            'particles5.w', 'particles6.w', 'particles7.w', 'particles8.w',
            'particles9.w', 'particles10.w']

    start = pd.datetime(yr, mth, day)
    end = start + timedelta(days=28)
    drange = pd.date_range(start, end, freq='30T')

    cols = np.arange(1, 1001, 1)

    partsLon = pd.DataFrame(0., index=drange, columns=cols)
    partsLat = pd.DataFrame(0., index=drange, columns=cols)

    for f in fils:
        print('\nReading {}'.format(os.path.join(path, f)))
        tmp = pd.read_csv(os.path.join(path, f), delim_whitespace=True,
                          header=None, parse_dates=[[1, 2, 3, 4]],
                          usecols=[0, 1, 2, 3, 4, 5, 6])
        tmp.columns = ['date', 'particle', 'x', 'y']
        print('Converting from UTM to lat/lon')
        x = tmp.x + xMin
        y = tmp.y + yMin
        lat, lon = utm.to_latlon(x, y, 14, 'R')
        tmp['lon'] = lon
        tmp['lat'] = lat
        tmpLat = tmp.pivot(index='date', columns='particle', values='lat')
        tmpLon = tmp.pivot(index='date', columns='particle', values='lon')
        partsLon.ix[tmpLon.index, tmpLon.columns] = tmpLon
        partsLat.ix[tmpLat.index, tmpLat.columns] = tmpLat

    return partsLon, partsLat
