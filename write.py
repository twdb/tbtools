'''Writing TxBLEND input/output files'''

import pandas as pd
import os

def gensal(df, out_path, loc_string):
    '''
    Write the TxBLEND boundary salinity concentration input file
    
    Parameters
    ----------
    df : dataframe
        Dataframe of the interpolated salinity values
        *must have a continuous, bihourly index
    out_path : string
        location where the file will be saved plus file name
    loc_string : string
        location string to indicate where the salinity data was colleged
        *e.g. 'OffGalves'
        
    Example
    -------
    import tbtools as tbt
    
    tbt.write.gensal(data, 'desired/output/path', 'OffGalves')
    
    Returns
    -------
    None
    '''
    fout = open(out_path,'w')
    for i in range(0,len(df),12):
        fout.write('%3i%3i%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6i %8s\n' % 
                  (df.index[i].month,df.index[i].day,
                   df.salinity[i],df.salinity[i+1],
                   df.salinity[i+2],df.salinity[i+3],
                   df.salinity[i+4],df.salinity[i+5],
                   df.salinity[i+6],df.salinity[i+7],
                   df.salinity[i+8],df.salinity[i+9],
                   df.salinity[i+10],df.salinity[i+11],
                   df.index[i].year,loc_string))
    fout.close()
    
def tide(df, out_path):
    '''
    Write the TxBLEND tide input file
    
    Parameters
    ----------
    df : dataframe
        Dataframe of the bihourly tide data
        *must have a continuous, bihourly index
    out_path : string
        location where the file will be saved plus file name
        
    Example
    -------
    import tbtools as tbt
    
    tbt.write.tide(data, 'desired/output/path')
    
    Returns
    -------
    None
    '''
    fout = open(out_path,'w')
    col = df.columns[0]
    for i in range(0,len(df),12):
        fout.write('%3i%3i%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f'
                   '%6.2f%6.2f%6.2f%6.2f%6.2f%6.2f%6i %-8s\n' % 
                  (df.index[i].month,df.index[i].day,
                   df[col][i],df[col][i+1],
                   df[col][i+2],df[col][i+3],
                   df[col][i+4],df[col][i+5],
                   df[col][i+6],df[col][i+7],
                   df[col][i+8],df[col][i+9],
                   df[col][i+10],df[col][i+11],
                   df.index[i].year,col))
    fout.close()
    
    