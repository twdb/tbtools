''' Reading TxBLEND input/output files '''

import pandas as pd
from io import StringIO
import re
import os
import numpy as np
import utm

def inflow(fil):
    '''
    Read contents of TxBLEND freshwater inflow file
    
    Parameters
    ----------
    fil : string
        File path
    
    Example
    -------
    import tbtools as tbt
    
    inflow = tbt.read.inflow(fil)
    
    Returns
    -------
    inflow : DataFrame
        Single column DataFrame with datetime index
    '''
    f = open(fil)
    s = StringIO()
    mergedLine = None
    for ln in f:
        if not ln.strip():
            continue
        if ln[0] == '#':
            continue
        if len(ln.split(',')) == 3: 
            mergedLine = ','.join(ln.split(',')[:2]).replace('\n', ',', 1) + ','
            continue
        if ln[12] != '3':
            mergedLine += ','.join(ln.replace('\n', ',', 1).split()[3:])
            continue
        else:
            mergedLine += ','.join(ln.split()[3:]) + '\n'
        s.write(mergedLine)
    
    s.seek(0)
    cols = ['year', 'month'] + ['{:02d}'.format(i) for i in range(1, 32, 1)]
    df = pd.read_csv(s, names=cols)
    inflow = pd.melt(df, 
                     id_vars=['year', 'month'],
                     value_vars=df.columns[2:].tolist(),
                     var_name='day')
    inflow.dropna(inplace=True)
    inflow['date'] = pd.to_datetime(inflow[['year', 'month', 'day']])
    inflow.index = inflow['date']
    inflow.drop(['year', 'month', 'day', 'date'], 1, inplace=True)
    inflow.columns = ['inflow_cfs']
    inflow.sort_index(inplace=True)
    
    return(inflow)
    
    
def precip(fil):
    '''
    Read contents of TxBLEND precipitation input file
    
    Parameters
    ----------
    fil : string
        File path
    
    Example
    -------
    import tbtools as tbt
    
    precip = tbt.read.precip(fil)
    
    Returns
    -------
    precip : DataFrame
        Single column DataFrame with datetime index
    '''
    f = open(fil)
    s = StringIO()
    mergedLine = None
    for ln in f:
        if not ln.strip():
            continue
        if ln[0] == '#':
            continue
        if len(ln.split(',')) == 3:
            mergedLine = ','.join(ln.split(',')[:2]).replace('\n', ',', 1) + ','
            continue
        if ln[12] != '3':
            mergedLine += ','.join(ln.replace('\n', ',', 1).split()[3:])
            continue
        else:
            mergedLine += ','.join(ln.split()[3:]) + '\n'
        s.write(mergedLine)
    s.seek(0)
    cols = ['year', 'month'] + ['{:02d}'.format(i) for i in range(1, 32, 1)]
    df = pd.read_csv(s, names=cols)
    precip = pd.melt(df, 
                     id_vars=['year', 'month'],
                     value_vars=df.columns[2:].tolist(),
                     var_name='day')
    precip.dropna(inplace=True)
    precip['date'] = pd.to_datetime(precip[['year', 'month', 'day']])
    precip.index = precip['date']
    precip.drop(['year', 'month', 'day', 'date'], 1, inplace=True)
    precip.columns = ['precip_inches']
    precip.sort_index(inplace=True)
    
    return(precip)


def wind(fil):
    '''
    Read contents of TxBLEND wind input file
    
    Parameters
    ----------
    fil : string
        File path
    
    Example
    -------
    import tbtools as tbt
    
    wind = tbt.read.wind(fil)
    
    Returns
    -------
    wind : DataFrame
        Dataframe with datetime index
            Columns:
                dir - Wind Direction (degrees from north)
                spd - Wind speed (miles per hour)
    '''
    cols = ['year', 'month', 'day', 'site', 'var'] + ['{:02d}'.format(i) for i in range(24)]
    df = pd.read_csv(fil, sep='\s+', names=cols, na_values='-9')
    wind = pd.melt(df,
                   id_vars=['year', 'month', 'day', 'site', 'var'],
                   value_vars=df.columns[5:].tolist(),
                   var_name='hour')
    wind['date'] = pd.to_datetime(wind[['year', 'month', 'day', 'hour']], errors='coerce')
    wind.index = wind['date']
    wind = (wind.drop(['year', 'month', 'day', 'hour', 'site'], 1)
            .pivot_table(index=['date'], columns='var', values='value'))
    wind.columns=['dir', 'spd']
    wind.dir *= 10
    
    return(wind)
    
   
def gensal(fil):
    '''
    Read contents of TxBLEND generated salinity input file
    
    Parameters
    ----------
    fil : string
        File path
        
    Example
    -------
    import tbtools as tbt
    
    gensal = tbt.read.gensal(fil)
    
    Returns
    -------
    gensal : DataFrame
        Single column DataFrame with datetime index
    '''
    cols = ['month', 'day'] + ['{:02d}'.format(i) for i in range(0, 24, 2)] + ['year', 'label']
    df = pd.read_csv(fil, sep='\s+', names=cols)
    gensal = pd.melt(df,
                     id_vars=['year', 'month', 'day'],
                     value_vars=df.columns[2:14].tolist(),
                     var_name='hour')
    gensal['date'] = pd.to_datetime(gensal[['year', 'month', 'day', 'hour']])
    gensal.index = gensal['date']
    gensal.drop(['year', 'month', 'day', 'hour', 'date'], 1, inplace=True)
    gensal.sort_index(inplace=True)
    gensal.columns=['salinity']
    
    return(gensal)
    
    
def pcp(fil):
    '''
    Read the *.pcp files created as an input for TxRR
        These are used to create the TxBLEND precip input files
        ***be sure you have the correct watershed pcp file***
        
    Parameters
    ----------
    fil : string
        File path
        
    Example
    -------
    import tbtools as tbt
    
    pcp = tbt.read.pcp(fil)
    
    Returns
    -------
    pcp : DataFrame
        Single column Dataframe with datetime index
    '''
    def chunkstring(string, length):
        return (string[0+i:length+i] for i in range(0, len(string), length))
    f = open(fil)
    s = StringIO()
    mergedLine = None
    for ln in f:
        #print ln
        if not ln.strip():
            continue
        if ln[0] == '#':
            continue
        if ln[0] == '1':
            #ln = ln.replace('\n', ',', 1)
            ws = ln[4:9]
            mergedLine = (ln[4:9] + ',' + ln[9:13] + ',' + ln[13:15] + ',' + \
                          ','.join(list(chunkstring(ln[17:], 8))).replace('\n', '', 1))
            continue
        if ln[0] in ['2', '3']:
            mergedLine += ','.join(list(chunkstring(ln[1:], 8))).replace('\n', '', 1)
            continue
        if ln[0] == '4':
            mergedLine += ','.join(list(chunkstring(ln[1:], 8))[:-2]) + '\n'
        s.write(mergedLine)
    s.seek(0)
    cols = ['ws', 'year', 'month'] + ['{:02d}'.format(i) for i in range(1,32,1)]
    df = pd.read_csv(s, names=cols, index_col=None, na_values='-9999.00')
    pcp = pd.melt(df,
                  id_vars=['ws', 'year', 'month'],
                  value_vars=df.columns[3:].tolist(),
                  var_name='day')
    pcp.dropna(inplace=True)
    pcp['date'] = pd.to_datetime(pcp[['year', 'month', 'day']])
    pcp.index = pcp['date']
    pcp.drop(['ws', 'year', 'month', 'day', 'date'], 1, inplace=True)
    pcp.columns = [(ws + '_pcp').strip()]
    pcp.sort_index(inplace=True)
    pcp.index.name = 'Date'
    return(pcp)
    

def vel(fil):
    '''
    Read the velx and vely files created while running TxBLEND
        
    Parameters
    ----------
    fil : string
        File path
        
    Example
    -------
    import tbtools as tbt
    
    vel = tbt.read.vel(fil)
    
    Returns
    -------
    vel : DataFrame
        Single column Dataframe with datetime index
    '''
    f = open(fil)
    s = StringIO()
    mergedLine = None
    init = 0
    for ln in f:
        if not ln.strip():
            continue
        if ln.split()[0] == 'Average':
            if init != 0:
                mergedLine = mergedLine[:-1]
                mergedLine += '\n'
                s.write(mergedLine)
            date = str(pd.datetime(int(ln.split()[4]), int(ln.split()[6]), int(ln.split()[8])))
            mergedLine = date + ','
            init = 1
            continue
        elif re.search('[a-zA-Z]', ln):
            continue
        else:
            mergedLine += ','.join(ln.split()).replace('\n', '', 1)
            mergedLine += ','
            continue
    mergedLine = mergedLine[:-1]
    mergedLine += '\n'
    s.write(mergedLine)
    s.seek(0)
    vel = pd.read_csv(s, parse_dates=True, index_col=0, header=None)
    vel.index.name = 'Date'
    return(vel)
    
    
def avesalD(fil):
    '''
    Read the average daily salinity file created while running TxBLEND
        ***NOTE: this is for the avesalD.w file (avesal.w is month average salinity)
        
    Parameters
    ----------
    fil : string
        File path
        
    Example
    -------
    import tbtools as tbt
    
    avesalD = tbt.read.avesalD(fil)
    
    Returns
    -------
    avesalD : DataFrame
        Single column Dataframe with datetime index
    '''
    f = open(fil)
    s = StringIO()
    mergedLine = None
    init = 0
    for ln in f:
        if not ln.strip():
            continue
        if ln.split()[0] == 'Average':
            if init != 0:
                mergedLine = mergedLine[:-1]
                mergedLine += '\n'
                s.write(mergedLine)
            date = str(pd.datetime(int(ln.split()[4]), int(ln.split()[6]), int(ln.split()[8])))
            mergedLine = date + ','
            init = 1
            continue
        elif re.search('[a-zA-Z]', ln):
            continue
        else:
            mergedLine += ','.join(ln.split()).replace('\n', '', 1)
            mergedLine += ','
            continue
    mergedLine = mergedLine[:-1]
    mergedLine += '\n'
    s.write(mergedLine)
    s.seek(0)
    avesalD = pd.read_csv(s, parse_dates=True, index_col=0, header=None)
    avesalD.index.name = 'Date'
    return(avesalD)
    
    
def outflw1(path=''):
    '''
    Read the contents of TxBLEND output file outflw1 (old format - no year)
        outflw1 contains hourly output at check nodes specified in input file
    
    Parameters
    ----------
    path : string (or empty string)
        Path to directory containing outflw1 and input files
        *if path is an empty string, will look for files in current working directory
        
    Example
    -------
    >>> import tbtools as tbt
    >>> outflw1 = tbt.read.outflw1(path)
    >>> outflw1
    {'10505':                      tide  elevation  depth  velocity  direction  salinity
     Date                                                                      
     2001-01-01 00:00:00  0.40       0.02   8.02      0.03     226.86      4.82
     2001-01-01 01:00:00 -0.18       0.07   8.07      0.02     226.86      4.79
     2001-01-01 02:00:00 -0.80       0.15   8.15      0.05      46.86      4.75
    ...
    
    >>> outflw1['1505']
                         tide  elevation  depth  velocity  direction  salinity
    Date                                                                      
    2001-01-01 00:00:00  0.40       0.02   8.02      0.03     226.86      4.82
    2001-01-01 01:00:00 -0.18       0.07   8.07      0.02     226.86      4.79
    2001-01-01 02:00:00 -0.80       0.15   8.15      0.05      46.86      4.75
    ...
    
    
    Returns
    -------
    outflw1 : Dictionary
        keys are the check nodes
        values are the dataframes for each check node
    '''
    #get the starting year (old outflw1 format)
    if path == '':
        fin1 = open('input')
    else:
        fin1 = open(os.path.join(path, 'input'))
    s = fin1.readline()
    while 'starting date of simulation' not in s:
        s = fin1.readline()
    s = s.replace(' ','').split(',')
    year = int(s[2][:4])
    fin1.close()
    #read off 5 lines - don't need them
    f = open(os.path.join(path,'outflw1'))
    for i in range(5):
        next(f)
    #create dictionary for StringIO 
    sio = {}
    init = 0
    
    for ln in f:
        if not ln.strip():
            init = 1
            if s[0] == '12' and s[1] == '31' and s[2] == '23.0':
                year += 1
            continue
        else:
            s = ln.split()
            #if first time through need to initialize StringIO objects
            if init == 0:
                sio[s[3]] = StringIO()
                sio[s[3]].write(str(year) + '-' + s[0] + '-' + s[1] + ' ' + s[2].split('.')[0] + ':00:00' + ',')
            else:
                sio[s[3]].write(str(year) + '-' + s[0] + '-' + s[1] + ' ' + s[2].split('.')[0] + ':00:00' + ',')
            sio[s[3]].write(','.join(s[4:8]) + ',')
            if len(s) == 11:
                sio[s[3]].write(','.join(s[9:]) + '\n')
            else:
                sio[s[3]].write(','.join([s[8][2:],s[9]]) + '\n')
            continue
            
    outflw1 = {}
    
    for k in list(sio.keys()):
        sio[k].seek(0)
        outflw1[k] = pd.read_csv(sio[k], parse_dates=True, index_col=0,
               names = ['tide', 'elevation', 'depth', 'velocity', 'direction', 'salinity'])
        outflw1[k].index.name = 'Date'
        
    return(outflw1)
    
    
def coords(fil, zone_number=14, out_type='ll'):
    '''
    Read node coordinates from TxBLEND input file and return the coordinates
    in either UTM projection northing/easting or latitude/longitude in decimal degrees
    
    Parameters
    ----------
    fil : string
        File path to TxBLEND input file
    zone_number : integer
        longitudinal projection zones
        Default is 14 for most of Texas Coast, use 15 if working in Galveston or Sabine
    out_type : string
        'll' will return latitude/longitude coordinates in decimal degrees
        'utm' will return utm northing/easting coordinates in feet
        'both' will return both (utm, latlon)
        
    Example
    -------
    import tbtools as tbt
    
    latlon = tbt.read.coords(fil, 14, 'll')
    utm = tbt.read.coords(fil, 15, 'utm')
    utm, latlon = tbt.read.coords(fil, 14, 'both')
    
    Returns
    -------
    coords : DataFrame
        index is node number
        columns are latitude/longitude or northing/easting
    '''
    f = open(fil, 'r')
    s = f.readline()
    while s.split()[0] != 'NN':
        s = f.readline()
    s = f.readline()
    nn = int(s[:5])
    while s.split()[0] != 'NODAL':
        s = f.readline()
    easting = np.zeros(nn)
    northing = np.zeros(nn)
    
    for i in range(nn):
        s = f.readline().split()
        easting[i] = float(s[1])
        northing[i] = float(s[2])
    lat, lon = utm.to_latlon(easting, northing, zone_number, 'R')
    
    coords_ll = pd.DataFrame(np.nan, index=range(1, nn+1, 1), columns=['lat', 'lon'])
    coords_utm = pd.DataFrame(np.nan, index=range(1, nn+1, 1), columns=['easting', 'northing'])
    
    coords_ll['lat'] = lat
    coords_ll['lon'] = lon
    coords_utm['easting'] = easting
    coords_utm['northing'] = northing
    
    if out_type == 'll':
        return(coords_ll)
    elif out_type == 'utm':
        return(coords_utm)
    elif out_type == 'both':
        return(coords_utm, coords_ll)
    else:
        print('WARNING: Bad out_type {0}, defaulting to lat/lon'.format(out_type))
        return(coords_ll)
    