from data_retriver import Bpm 

bpm_url = "https://ps-irrad.web.cern.ch/irrad/bpm.php?bpmid=BPM_0"

deviation = .3

def check_bpm():
  # BPMs are numbered 1 through 4
  # index 0 contains refrence data,
  # and the last index contains the most recent sampling
  b = Bpm()
  for i in range(1,5):
    data = b.dl_bpm_data(bpm_url+str(i))
    xdata = b.extract_xy_data(data['X'])
    ydata = b.extract_xy_data(data['Y'])
    for j in  ('intensity','fwhm'):
      if ((xdata[-1][j] > (1+deviation)*xdata[0][j]) or (xdata[-1][j] < (1-deviation)*xdata[0][j])):
        print("Large deviation in the " + j + " of BPM" + str(i))
        print(" reference " + j + " " + str(xdata[0][j]))
        print(" current " + j + " " + str(xdata[0][j]))
check_bpm()
