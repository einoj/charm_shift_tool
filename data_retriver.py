from urllib import request
import re
import json
from pprint import pprint
from scipy.optimize import curve_fit
import numpy as np
from archive.database_call_v0 import lgdb_tools
from datetime import datetime, timedelta
import pandas as pd

bpm_url = "https://ps-irrad.web.cern.ch/irrad/bpm.php?bpmid=BPM_0"
tf = '%Y-%m-%d %H:%M:%S'

def fwhm(sigma):
  return round(sigma*2.355,2)

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
      xdata = self.extract_xy_data(data['X'])
      ydata = self.extract_xy_data(data['Y'])
    return xdata, ydata

  
class MWPC:
  def gaussian_fit_test(self,x_data,y_data):
      y_offset = np.min(y_data)
      x = np.array(x_data)
      y = np.array(y_data)-y_offset

      x_fine = np.arange(-100, 100, 0.1)  # x array, with finer resolution
      p = [1.0, 1.0, 75.0]             # initial fit params
      coeff, pcov = curve_fit(gauss, x, y, p) # fit the params, get coeffs
      y_fit = gauss(x_fine, *coeff)+y_offset                      # make a nice gaussian with fine x array

      peak,     centre,     sigma     = coeff
      peak_err, centre_err, sigma_err = np.sqrt(np.diag(pcov))

      fwhm = 2.355*sigma
      err_sigma  = (sigma_err/sigma)*100                    # std/sigma, % error for the FWHM value
      return x_fine, y_fit, fwhm, err_sigma, centre, centre_err

  def read_mwpc(self, filename, t_target, n_spills):
      filename = './data/{}.csv'.format(filename)

      headers = ['Time [local]']+[i for i in range(32)]
      df = pd.read_csv(filename, delimiter=',', names=headers, index_col=False, skiprows=8)
      df['Time [local]'] = pd.to_datetime(df['Time [local]'])
      df = df.set_index('Time [local]')
      df = df[:t_target][-n_spills:]
      return df

  def get_mwpc_data(self):
    n_spills = 10
    vdata, hdata = self.fetch_from_timber()

    vdata_s = vdata.sum()
    vdata_d = vdata.std(axis=0)
    hdata_s = vdata.sum()
    hdata_d = vdata.std(axis=0)

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

    x_f, y_f, fwhm, err_sigma, centre, centre_err = self.gaussian_fit_test(vx, vy)
    fwhm_v = fwhm

    x_f, y_f, fwhm, err_sigma, centre, centre_err = self.gaussian_fit_test(hx, hy)
    fwhm_h = fwhm

    v_intensity = vdata.ix[-1].max()
    h_intensity = hdata.ix[-1].max()

    return v_intensity, h_intensity, fwhm_v, fwhm_h


  def fetch_from_timber(self):
    variable_name_h = 'MWPC.ZT8.135:PROFILE_H'
    variable_name_v = 'MWPC.ZT8.135:PROFILE_V'

    filename_v = 'mwpc_v'
    filename_h = 'mwpc_h'

    t1 = (datetime.now()-timedelta(hours=1)).strftime(tf)
    #t1 = '2015-05-18 20:00:00'
    t_now = (datetime.now()).strftime(tf)
    #t2 = '2015-05-20 06:00:00'

    t_check = t_now
    #t_check = '2015-05-26 06:00:01'

    a = lgdb_tools()
    output1 = a.get_data(variable_name_h, t1, t_now, filename_h)
    output2 = a.get_data(variable_name_v, t1, t_now, filename_v)

    n_spills = 10

    vdata = self.read_mwpc(filename_v, t_check, n_spills)
    hdata = self.read_mwpc(filename_h, t_check, n_spills)

    return vdata, hdata 
