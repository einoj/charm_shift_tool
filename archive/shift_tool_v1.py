import numpy as np
import pandas as pd
import json
import urllib2
import matplotlib.pylab as plt
import matplotlib.dates as md
from database_call_v0 import lgdb_tools
from datetime import datetime, timedelta
import time
import re
from email_tools import alert
tf = '%Y-%m-%d %H:%M:%S'

calibration = {
    'SEC1': 2.2E7
}

def main():

    while True:
        now = roundTime(datetime.now(), roundTo=60*60)
        t1 = (now-timedelta(hours=2)).strftime(tf)
        t2 = (now).strftime(tf)
        output = get_pot(t1, t2)



        pot_df = analyse_pot()
        try:
            last_spill = pot_df.index[-1]
            warning = '{} - PROBLEM! NO BEAM SINCE {}!'.format(datetime.now(), last_spill)
        except IndexError:
            last_spill = datetime.strptime(t1, tf)
            warning = '{} - PROBLEM! NO BEAM FOR OVER 2 HOURS!'.format(datetime.now())

        d = (now-last_spill)
        if d.seconds>(45.0*60):
            print(warning)
            alert('CHARM No Beam!', warning)
        else:
            print('{} - BEAM CHECK OK!'.format(now))

        time.sleep(60*60)


def get_pot(t1, t2):
    a = lgdb_tools()
    variable_name = 'MSC01.ZT8.107:COUNTS'
    filename = 'sec1_data'
    output = a.get_data(variable_name, t1, t2, filename)
    return output

def analyse_pot():
    df = pd.read_csv('./data/sec1_data.csv',
                     delimiter=',', names=['Time [local]','Counts'],index_col=False, skiprows=8)
    df = df[df.Counts.notnull()]
    df['Time [local]'] = pd.to_datetime(df['Time [local]']) # check the timing, seems to be off
    df = df.set_index('Time [local]')
    df['pot/spill'] = df['Counts'].values*calibration['SEC1']
    t_pot = df['pot/spill'].sum()

    return df

def roundTime(dt=None, roundTo=60):
    '''
    Round a datetime object to any time laps in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    '''

    if dt == None: dt = datetime.now()
    seconds = (dt - dt.min).seconds
    # // is a floor division, not a comment on following line:
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + timedelta(0,rounding-seconds,-dt.microsecond)

def get_fluka(value, config):
    url = 'http://thornton.web.cern.ch/thornton/cgi-bin/data_api_v0.py?value={}&config={}&norm=1'
    data = json.load(urllib2.urlopen(url.format(value, config)))
    fluka_est = data['Data']
    return fluka_est

if __name__ == "__main__":
    main()
