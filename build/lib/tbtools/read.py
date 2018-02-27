''' Reading TxBLEND input/output files '''

import pandas as pd
from io import StringIO
import re
import os
import numpy as np
import utm
import sys
import datetime as dt

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
            #mergedLine += ','.join(ln.replace('\n', ',', 1).split()[3:])
            mergedLine += ','.join([ln[13:][i:i+6] for i in range(0, len(ln[13:]), 6)][:-1]) + ','
            continue
        else:
            #mergedLine += ','.join(ln.split()[3:]) + '\n'
            mergedLine += ','.join([ln[13:][i:i+6] for i in range(0, len(ln[13:]), 6)][:-1]) + '\n'
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


def tide(fil):
    '''
    Read contents of TxBLEND tide input file

    Parameters
    ----------
    fil : string
        File Path

    Example
    -------
    import tbtools as tbt

    gensal = tbt.read.tide(fil)

    Returns
    -------
    tide : DataFrame
        Single column DataFrame with datetime index
    '''
    cols = ['month', 'day'] + ['{:02d}'.format(i) for i in range(0, 24, 2)] \
        + ['year', 'label']
    df = pd.read_csv(fil, sep='\s+', names=cols)
    tide = pd.melt(df,
                   id_vars=['year', 'month', 'day'],
                   value_vars=df.columns[2:14].tolist(),
                   var_name='hour')
    tide['date'] = pd.to_datetime(tide[['year', 'month', 'day', 'hour']])
    tide.index = tide['date']
    tide.drop(['year', 'month', 'day', 'hour', 'date'], 1, inplace=True)
    tide.sort_index(inplace=True)
    tide.columns = ['salinity']

    return tide


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


def extfd(fs='', var=''):
    '''
    Extract data from intensive field surveys for use in TxBLEND validation.
    For now (v0.5) will only work on Windows machines with archive mounted as F:

    Parameters
    ----------
    fs : int
        This is the integer id of the field surveys:
            1 - CorpusChristi94
            2 - Christmas92
            3 - Programs
            4 - CopanoAransas88
            5 - ULM95
            6 - EastMat
            7 - Galveston89
            8 - Sanantonio88
            9 - LagunaMadre91
            10 - Sabine96
            11 - CorpusChristi87
            12 - Aransas95
            13 - Matagorda93
            14 - Nueces98
            15 - LLM97
            16 - Matagorda88
            17 - Sabine90
            18 - Aransas99
    var : string
        This is the length one string of the variable needed
            V - Velocity
            T - Tides
            S - Salinity
            D - Discharge

    Example
    -------
    import tbtools as tbt

    data = tbt.read.extfd(1, 'V')

    Returns
    -------
    data : DataFrame
        index is the datetime
        columns are specific to the variable (var) selected
    '''
    path = 'F:\\share\\archive\\Fieldstudies\\'
    site = os.listdir(path)[fs-1]
    path = os.path.join(path,site)
    if var.lower() == 'd':
        if 'ADCP' not in os.listdir(path):
            sys.exit('Incorrect structure - import data manually')
        path = os.path.join(path,'ADCP')
        for i in os.listdir(path):
            if 'Summary' in i:
                path = os.path.join(path,i)
        if path[-4:] == 'ADCP':
            sys.exit('Incorrect structure - import data manually')
        for i in range(len(os.listdir(path))):
            if os.listdir(path)[i][:5] == 'flow.':
                path = os.path.join(path,os.listdir(path)[i])
                break
        if path[-4:] == 'Summ':
            sys.exit('Incorrect structure - import data manually')
        fin = open(path)
        s = fin.readline()
        disch = []
        s = fin.readline()
        while s.split() != []:
            s = s.split()
            if len(s[2]) == 2:
                date = dt.datetime(int('19'+s[1][:2]),int(s[1][2:4]),int(s[1][4:]),0,int(s[2]))
            elif len(s[2]) == 3:
                date = dt.datetime(int('19'+s[1][:2]),int(s[1][2:4]),int(s[1][4:]),int(s[2][0]),int(s[2][-2:]))
            else:
                date = dt.datetime(int('19'+s[1][:2]),int(s[1][2:4]),int(s[1][4:]),int(s[2][:2]),int(s[2][-2:]))
            disch.append([date,int(s[0]),int(s[3])])
            s = fin.readline()
        dischdf = pd.DataFrame(disch,columns=['Date','Station','Discharge'])
        dischdf.index = dischdf.Date
        dischdf.pop('Date')
        return dischdf

    if var.lower()=='v':
        if 'Velocity' not in os.listdir(path):
            sys.exit('ERR1 - Incorrect structure - import data manually')
        #path+='Velocity/'
        path = os.path.join(path,'Velocity')
        print(path)
        x=0
        for i in range(len(os.listdir(path))):
            if os.listdir(path)[i][:4]=='vel.':
                #path+=os.listdir(path)[i]
                path = os.path.join(path,os.listdir(path)[i])
                x+=1
                break
        if x==0:
            sys.exit('ERR2 - Incorrect structure - import data manually')
        fin=open(path)
        s=fin.readline()
        if s.split()[4].lower()!='v8':
            sys.exit('ERR3 - sIncorrect structure - import data manually')
        s=fin.readline()
        vel=[]
        while s.split()!=[]:
            s=s.split()
            s2='0000'+s[2]
            if int(s2[-4:-2])<=23:
                vel.append([dt.datetime(int('19'+s[1][:2]),int(s[1][2:4]),int(s[1][4:]),
                    int(s2[-4:-2]),int(s2[-2:])),s[0],float(s[4]),float(s[5]),float(s[6])])
            s=fin.readline()
        veldf=pd.DataFrame(vel,columns=['Date','Station','v8','v5','v2'])
        veldf.index = veldf.Date
        veldf.pop('Date')
        return veldf

    if var.lower()=='t':
        if 'Tides' not in os.listdir(path):
            sys.exit('Incorrect structure - import data manually')
        #path+='Tides/'
        path = os.path.join(path,'Tides')
        x=0
        for i in range(len(os.listdir(path))):
            if os.listdir(path)[i][:6]=='tides.':
                #path+=os.listdir(path)[i]
                path = os.path.join(path,os.listdir(path)[i])
                x+=1
                break
        if x==0:
            sys.exit('Incorrect stucture - import data manually')
        fin=open(path)
        title=fin.readline()
        s=fin.readline()
        tide=[]
        while s.split()!=[]:
            s=s.split()
            for hr in range(12):
                if float(s[hr+4])!=-9.99:
                    tide.append([dt.datetime(int(s[1]),int(s[2]),int(s[3]),hr),
                        s[0],float(s[hr+4])])
            s=fin.readline().split()
            for hr in range(12,24):
                if float(s[hr-8])!=-9.99:
                    tide.append([dt.datetime(int(s[1]),int(s[2]),int(s[3]),hr),
                        s[0],float(s[hr-8])])
            s=fin.readline()
        tidedf=pd.DataFrame(tide,columns=['Date','Station','Elevation'])
    #    return tidedf
        fin.close()

    if var.lower()=='s':
        if 'Quality' not in os.listdir(path):
            sys.exit('Incorrect structure - import data manually')
        #path+='Quality/'
        path = os.path.join(path,'Quality')
        x=0
        anc=0
        for i in range(len(os.listdir(path))):
            if os.listdir(path)[i][:5]=='qual.':
                if os.listdir(path)[i][-9:]=='ancillary':
                    anc=1
                    #pathanc=path+os.listdir(path)[i]
                    pathanc = os.path.join(path,os.listdir(path)[i])
                else:
                    #path1=path+os.listdir(path)[i]
                    path1 = os.path.join(path,os.listdir(path)[i])
                    x+=1
                    break
        for i in range(len(os.listdir(path))):
            if os.listdir(path)[i][:7]=='sondes.':
                #path2=path+os.listdir(path)[i]
                path2 = os.path.join(path,os.listdir(path)[i])
                x+=3
                break
        if x==0:
            sys.exit('Incorrect structure - import data manually')
        elif x==1:
            print('qual. file OK\nsondes. file missing or incorrect structure - import data manually')
        elif x==3:
            print('sondes. file OK\nqual. file missing or incorrect structure - import data manually')
        if x==1 or x==4:
            fin1=open(path1)#qual.
            title=fin1.readline()
            s=fin1.readline()
            sal=[]
            while s.split()!=[]:
                s=s.split()
                s2='0000'+s[2]
                if int(s2[-4:-2])<=23:
                    if float(s[9])!=-9.99:
                        sal.append([dt.datetime(int(s[1][:2]),int(s[1][2:4]),int(s[1][4:]),
                            int(s2[-4:-2]),int(s2[-2:])),s[0],float(s[9])])
                s=fin1.readline()
        if anc==1:#if ancillary file exists
            financ=open(pathanc)
            title=financ.readline()
            s=financ.readline()
            while s.split()!=[]:
                s=s.split()
                s2='0000'+s[2]
                if int(s2[-4:-2])<=23:
                    if float(s[9])!=-9.99:
                        sal.append([dt.datetime(int(s[1][:2]),int(s[1][2:4]),int(s[1][4:]),
                            int(s2[-4:-2]),int(s2[-2:])),s[0],float(s[9])])
                s=financ.readline()
        if x==3 or x==4:
            fin2=open(path2)#sondes.
            head=[]
            if x==3:
                sal=[]
            if path[-6:]!='LLM97/':
                s=fin2.readline()
                while len(s)!=51 and len(s.split())!=8:
                    head.append(s)
                    s=fin2.readline()
                    if s[:4]=='D5:*':
                        head.append(s)
                        s=fin2.readline()
            else:
                s=fin2.readline()
                while len(s)!=58 and len(s.split())!=9:
                    head.append(s)
                    s=fin2.readline()
            t=s
            while s.split()!=[]:
                s=s.split()
                s2='0000'+s[2]
                if int(s2[-4:-2])<=23:
                    if float(s[6])!=-9.99:
                        sal.append([dt.datetime(int(s[1][:2]),int(s[1][2:4]),int(s[1][4:]),
                            int(s2[-4:-2]),int(s2[-2:])),s[0],float(s[6])])
                s=fin2.readline()
        saldf=pd.DataFrame(sal,columns=['Date','Station','Salinity'])
        return saldf,head
        fin1.close()
        fin2.close()

def extwq(site=''):
    '''
    Extract water quality data from TWDB Datasonde sites

    Parameters
    ----------
    site : string
        name (abbrev) of the site

    Example
    -------
    import tbtools as tbt

    data = tbt.read.extwq(site='MIDG')

    Returns
    -------
    wqdf : dataframe
        index is datetime
        single column - salinity
    '''
    if site == '':
        site = raw_input('Enter site name >> ')
    path = 'T:\\baysestuaries\\Data\\WQData\\sites'
    try:
        fin = open(os.path.join(path, site, 'twdb_wq_{}.csv'.format(site)))
    except IOError:
        try:
            fin = open(os.path.join(path, site, 'twdb_wq_{}_provisional.csv'.format(site)))
        except:
            raise OSError('No data found')
    s = fin.readline()
    while s[0] == '#':
        cols = s[2:].replace(' ', '').split(',')
        s = fin.readline()
    ind = cols.index('PSU')
    wqsal = []
    while s != []:
        s = s.split(',')
        x = dt.datetime.strptime(s[0], '%Y/%m/%d %H:%M:%S')
        if float(s[ind])!= -999.99:
            wqsal.append([x, float(s[ind])])
        s=fin.readline()
        if s==[] or s=='':
            break
    fin.close()
    wqdf = pd.DataFrame(wqsal, columns=['Date', 'Salinity'])
    wqdf.index = wqdf.Date
    wqdf.pop('Date')
    return wqdf

def tidesCBI(site, startY=1990, endY=2020, datum=0):
    '''
    Read the CBI tides for the specified site and the specified dates, datum

    Parameters
    ----------
    site : string
        Station name
    startY : int
        Start Year
    endY : int
        End Year (inclusive)
    datum : float
        datum to correct the tide data with (in feet)

    Example
    -------
    import tbtools as tbt

    data = tbt.read.tidesCBI('seadrift', 1997, 1998, 1.28)

    Returns
    -------
    tide : dataframes
        index is datetime
        column is observed tide (in ft)
    '''
    site = str.lower(site)
    tideDir = 'F:\\share\\archive\\Tides\\CBI'
    dates = []
    for y in range(startY, endY+1, 1):
        for m in range(1, 13, 1):
            dates += [(str(y), str(m).zfill(2))]

    init = 1

    for d in dates:
        if init == 1:
            if os.path.exists(os.path.join(tideDir, site, site + '.' + d[0]+ '.' + d[1])):
                tide = pd.read_csv(os.path.join(tideDir,site,site+'.'+d[0]+'.'+d[1]), sep='\s*',
                              skiprows=8, usecols=[1,2,3,4], header=None, engine='python',
                              converters={1:str, 2:str, 3:str, 4:float})
                tide.columns = ['yr', 'doy', 'time', 'tide_mm']
                tide.doy = tide.doy.str.zfill(3)
                tide.time = tide.time.str.zfill(4)
                tide['datestr'] = tide.yr + tide.doy + tide.time
                tide['date'] = pd.to_datetime(tide.datestr, format='%y%j%H%M')
                tide.index = tide.date
                tide = tide.drop(['yr', 'doy', 'time', 'datestr', 'date'], axis=1)
                init = 0
                print('File '+ site + '.' + d[0] + '.' + d[1] + ' read properly')
            else:
                print('No tide file called: ' + site + '.' + d[0] + '.' + d[1])
        else:
            if os.path.exists(os.path.join(tideDir, site, site + '.' + d[0]+ '.' + d[1])):
                tmp = pd.read_csv(os.path.join(tideDir,site,site+'.'+d[0]+'.'+d[1]), sep='\s*',
                                  skiprows=8, usecols=[1,2,3,4], header=None, engine='python',
                                  converters={1:str, 2:str, 3:str, 4:float})
                tmp.columns = ['yr', 'doy', 'time', 'tide_mm']
                tmp.doy = tmp.doy.str.zfill(3)
                tmp.time = tmp.time.str.zfill(4)
                tmp['datestr'] = tmp.yr + tmp.doy + tmp.time
                tmp['date'] = pd.to_datetime(tmp.datestr, format='%y%j%H%M')
                tmp.index = tmp.date
                tmp = tmp.drop(['yr', 'doy', 'time', 'datestr', 'date'], axis=1)
                tide = tide.append(tmp)
                print('File '+ site + '.' + d[0] + '.' + d[1] + ' read properly')
            else:
                print('No tide file called: ' + site + '.' + d[0] + '.' + d[1])
    if 'tide' not in vars():
        print('No tides available for this site for this time period!')
        return
    print('\n' + '#'*30)
    print('Tides read for ' + site + '\nStart: ' + str(tide.index[0]) + '\nEnd: ' + str(tide.index[-1]))
    print('#'*30)

    if datum == 0:
        print('\n***Tides were not corrected with datum***')
    else:
        print('\n***Tides were corrected with a datum of %.2f feet***' % datum)
    tide = tide.replace(-9999, pd.np.nan)
    tide['Elev'] = tide.tide_mm * 0.00328084 - datum
    tide = tide.drop('tide_mm', axis=1)
    return tide

def start_end(path):
    '''
    Read the start and end dates of a TxBLEND model run from the output file

    Parameters
    ----------
    path : string
        path to the directory where the TxBLEND run was run

    Example
    -------
    import tbtools as tbt

    start_date, end_date = tbt.read.start_end(r'T:/path/to/file')

    Returns
    -------
    start_date : datetime object
        starting date of simulation
    end_date : datetime object
        ending date of simulation
    '''
    fin = open(os.path.join(path, 'output'), 'r')
    s = fin.readline().replace('=', ' ').split()
    while s[0] != 'MNTH1':
        s = fin.readline().replace('=', ' ').split()
    start_date = dt.datetime(int(s[5]), int(s[1]), int(s[3]), 0)
    s = fin.readline().replace('=', ' ').split()
    end_date = dt.datetime(int(s[5]), int(s[1]), int(s[3]), 23)
    fin.close()
    return start_date, end_date

def outflw2(path):
    '''
    Read the outflw2 files (flow through passes)

    Parameters
    ----------
    path : string
        path to the directory where TxBLEND was run

    Example
    -------
    import tbtools as tbt

    outflw2 = tbt.read.outflw2(path)

    Returns
    -------
    outflw2 : dataframe
        index is datetime
        columns are passes
    '''
    #read the start and end date of the model
    start_date, end_date = start_end(path)
    #make sure we read all the outflw2 files
    outflw2_fils = []
    for fil in os.listdir(path):
        if fil[:7] == 'outflw2':
            outflw2_fils.append(fil)
    #now loop through the outflw2 files
    for i in range(len(outflw2_fils)):
        #if first iteration, save outflw2 data to dataframe "data"
        if i == 0:
            outflw2 = pd.read_csv(os.path.join(path, outflw2_fils[i]), sep='\s+', skiprows=6)
        #for any other outflw2 file, add the columns to the "data" dataframe
        else:
            tmp = pd.read_csv(os.path.join(path, outflw2_fils[i]), sep='\s+', skiprows=6)
            for col in tmp.columns[3:]:
                outflw2[col] = tmp[col]
    #sometimes, the model runs to the next hour past the end date, to fix
    #this need to try to reindex first. If that doesn't work, delete the last row
    #and try again
    try:
        outflw2.index = pd.date_range(start_date, end_date, freq='H')
    except:
        outflw2 = outflw2.drop(outflw2.index[-1])
        outflw2.index = pd.date_range(start_date, end_date, freq='H')
    else:
        print('Model dates do not match contents of outflw2 files')
        raise
    #now drop the month, day, and time columns
    outflw2 = outflw2.drop(['Mnth', 'Day', 'Time'], axis=1)
    return outflw2
