from urllib import request
import re
import json
from pprint import pprint
import numpy as np


def fwhm(sigma):
  return round(sigma*2.355,2)

class Bpm:

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
    s = np.sqrt(Q/W);
    return round(s,2)

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
  

