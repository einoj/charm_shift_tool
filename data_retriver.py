from urllib import request
import re
import json
from pprint import pprint
import numpy as np
from archive.database_call_v0 import lgdb_tools
from datetime import datetime, timedelta

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
    output1 = a.get_data(variable_name_v, t1, t_now, filename_v)

    n_spills = 10

    message1 = mwpc(filename_h, t_check, n_spills)
    message2 = mwpc(filename_v, t_check, n_spills)

    return message1, message2
