#! /usr/bin/env python

"""
Compute final base position and statistics
Input is pos file from RTKLIB

David Shean
dshean@gmail.com
"""

import os
import argparse
import numpy as np
import pandas as pd
from pygeotools.lib import geolib

#Hack to update solution status
def get_solution_status(Q):
    Q = np.round(Q)
    out = None
    if Q == 1.0: 
        out = 'FIX'
    elif Q == 2.0: 
        out = 'FLOAT'
    elif Q == 5.0:
        out = 'SINGLE'
    return out

def getparser():
    parser = argparse.ArgumentParser(description='Comptue base position from PPK position output from RTKLIB')
    parser.add_argument('ppk_pos_fn', type=str, help='PPK pos filename')
    return parser

def main():
    parser = getparser()
    args = parser.parse_args()

    ppk_pos_fn = args.ppk_pos_fn

    header = 'Date UTC latitude(deg) longitude(deg)  height(m)   Q  ns   sdn(m)   sde(m)   sdu(m)  sdne(m)  sdeu(m)  sdun(m) age(s)  ratio'
    print('Loading: %s' % ppk_pos_fn)
    ppk_pos = pd.read_csv(ppk_pos_fn, comment='%', delim_whitespace=True, names=header.split(), parse_dates=[[0,1]])

    #Add filter to include only fix positions

    #Compute statistics for pos
    ppk_pos_mean = ppk_pos.mean()
    ppk_pos_std = ppk_pos.std()
    ppk_pos_med = ppk_pos.median()
    ppk_pos_nmad = (abs(ppk_pos.drop('Date_UTC', axis=1) - ppk_pos_med)).median()
    ppk_pos_itrf = geolib.ll2itrf(ppk_pos_med['longitude(deg)'], ppk_pos_med['latitude(deg)'], ppk_pos_med['height(m)'])

    #Should format output to be mean +/- std in meters
    print("\nMean")
    print(ppk_pos_mean)
    print("\nStd")
    print(ppk_pos_std)
    print("\nMedian")
    print(ppk_pos_med)
    print("\nNMAD")
    print(ppk_pos_nmad)
    print("\nITRF")
    print(ppk_pos_itrf)

if __name__ == "__main__":
    main()
