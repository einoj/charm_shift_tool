from urllib import request
import re

bpm_url = "https://ps-irrad.web.cern.ch/irrad/bpm.php?bpmid=BPM_0"

def get_bpm_data():
  for i in range(1,5):
    html = request.urlopen(bpm_url+str(i)).read().decode("utf8")
    print (re.findall(r"startData =*;",html))
