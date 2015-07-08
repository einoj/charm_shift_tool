from urllib import request
import re
import json
from pprint import pprint
#from scipy.optimize import curve_fit
import numpy as np
from archive.database_call_v0 import lgdb_tools
from datetime import datetime, timedelta
import pandas as pd

bpm_url = "https://ps-irrad.web.cern.ch/irrad/bpm.php?bpmid=BPM_0"
tf = '%Y-%m-%d %H:%M:%S'

def fwhm(sigma):
  return round(sigma*2.355,2)

class Timber_detectors(object):
  def fetch_from_timber(self, variable_name, filename):
    a = lgdb_tools()
    t1 = (datetime.now()-timedelta(hours=1)).strftime(tf)
    t_now = (datetime.now()).strftime(tf)
    output = a.get_data(variable_name, t1, t_now, filename)
    return output

  def read_timber_data(self, filename, t_target, headers):
      filename = './data/{}.csv'.format(filename)
      df = pd.read_csv(filename, delimiter=',', names=headers, index_col=False, skiprows=8)
      df['Time [local]'] = pd.to_datetime(df['Time [local]'])
      df = df.set_index('Time [local]')
      return df

class BPM:

  def integralMean(self,data):
    weight = 0.0
    weightedSum = 0.0
    for arr in data:
      weight += arr[1]
      weightedSum += arr[1]*arr[0];
    if(weight == 0):
      return (0)
    return round(weightedSum/weight,2)

  def sigma(self, data,mean):
    W = 0.0
    Q = 0.0
    for arr in data:
      W += arr[1]
      Q += arr[1]*(arr[0]-mean)*(arr[0]-mean)
    try:
      s = np.sqrt(Q/W);
      return round(s,2)
    except ZeroDivisionError:
      return 0.0

  # Returns dictionary that contains reference data aswell as the last 
  # 4 time stamped samplings
  def dl_bpm_data(self, url):

    html = request.urlopen(url).read().decode("utf8")
    json_table = re.findall(r"startData = (.*);",html)[0]
    data_dict = json.loads(json_table)

    return data_dict

  #
  def extract_xy_data(self, data_dict):
      data_arr = []
      
       # i in data_dict are each a dictionary which contains
       # the data array on index 'data'. The data array is
       # devided into several smaller arrays each containing x and y values like this
       # [[x0,y0], [x1,y1], ..., [xn,yn]]
      for i in data_dict:
        data = {}
        data['title'] = i['title']
        data['mean']  = self.integralMean(i['data'])
        data['sigma'] = self.sigma(i['data'], data['mean'])
        data['fwhm'] = fwhm(data['sigma'])
        int_arr = []
        for j in i['data']:
          int_arr.append(j[1])
        data['intensity'] = max(int_arr)
        data_arr.append(data)

      return data_arr
  
  # returns the last samples from all the BPMs
  # both in the Y and X axis
  def get_bpm_data(self):
    xdata = []
    ydata = []
    for i in range(1,5):
      data = self.dl_bpm_data(bpm_url+str(i))
      xdata.append(self.extract_xy_data(data['X']))
      ydata.append(self.extract_xy_data(data['Y']))
    return xdata, ydata
  
class MWPC(Timber_detectors):

  def integralMean(self,x,y):
    weight = 0.0
    weightedSum = 0.0
    for i in range(len(x)):
      weight += y[i]
      weightedSum += y[i]*x[i];
    if(weight == 0):
      return (0)
    return round(weightedSum/weight,2)

  def sigma(self, x, y, mean):
    W = 0.0
    Q = 0.0
    for i in range(len(x)):
      W += y[i]
      Q += y[i]*(x[i]-mean)*(x[i]-mean)
    try:
      s = np.sqrt(Q/W);
      return round(s,2)
    except ZeroDivisionError:
      return 0.0

  def get_data(self):
    n_spills = 10
    variable_name_h = 'MWPC.ZT8.135:PROFILE_H'
    variable_name_v = 'MWPC.ZT8.135:PROFILE_V'
    filename_v = 'mwpc_v'
    filename_h = 'mwpc_h'
    headers = ['Time [local]']+[i for i in range(32)]

    self.fetch_from_timber(variable_name_v, filename_v)
    self.fetch_from_timber(variable_name_h, filename_h)

    t_now = (datetime.now()).strftime(tf)
    vdata = self.read_timber_data(filename_v, t_now, headers) 
    hdata = self.read_timber_data(filename_h, t_now, headers) 

    vdata = vdata[:t_now][-n_spills:]
    hdata = hdata[:t_now][-n_spills:]

    vdata_s = vdata.sum()
    vdata_d = vdata.std(axis=0)
    hdata_s = hdata.sum()
    hdata_d = hdata.std(axis=0)

    v_start = str(vdata.index[0]).split('.')[0]
    v_end   = str(vdata.index[-1]).split('.')[0]
    h_start = str(hdata.index[0]).split('.')[0]
    h_end   = str(hdata.index[-1]).split('.')[0]

    spacing = 6.0 # mm
    Lv = spacing*len(vdata_s.T)
    v_y_max = vdata_s.max().max()
    Lh = spacing*len(hdata_s.T)
    h_y_max = hdata_s.max().max()

    vx = ((np.array(vdata_s.index))*spacing)-(Lv/2.0)+(spacing/2)
    vy = vdata_s.values/n_spills
    hx = ((np.array(hdata_s.index))*spacing)-(Lh/2.0)+(spacing/2)
    hy = hdata_s.values/n_spills

    #fwhm_v = 2.355*np.std(vy)
    #x_f, y_f, fwhm, err_sigma, centre, centre_err = self.gaussian_fit_test(vx, vy)
    #fwhm_v = fwhm

    fwhm_v = 2.355*self.sigma(vx,vy,self.integralMean(vx,vy))
    fwhm_h = 2.355*self.sigma(hx,hy,self.integralMean(hx,hy))

    #fwhm_h = 2.355*np.std(hy)
    #x_f, y_f, fwhm, err_sigma, centre, centre_err = self.gaussian_fit_test(hx, hy)
    #fwhm_h = fwhm

    v_intensity = vdata.ix[-1].max()
    h_intensity = hdata.ix[-1].max()

    return v_intensity, h_intensity, fwhm_v, fwhm_h

class SEC(Timber_detectors):
  def __init__(self):
    self.calibration = {
        'SEC1': 2.2E7
    }
  def get_data(self):
    variable_name = 'MSC01.ZT8.107:COUNTS'
    filename = 'sec1_data'
    headers = ['Time [local]','Counts']

    self.fetch_from_timber(variable_name, filename)
    t_now = (datetime.now()).strftime(tf)
    data = self.read_timber_data(filename, t_now, headers)
    data['pot/spill'] = data['Counts'].values*self.calibration['SEC1']
    return data
