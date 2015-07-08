from data_retriver import BPM, MWPC, SEC
from datetime import datetime, timedelta

deviation = .3

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

def check_BPM():
  # BPMs are numbered 1 through 4
  # index 0 contains refrence data,
  # and the last index contains the most recent sampling
  b = BPM()
  ret_str  = ""
  xdata, ydata = b.get_bpm_data()
  for i in range(len(xdata)):
    for j in  ('intensity','fwhm'):
      if j == 'fwhm':
        print ("FWHM = " + str(xdata[i][-1][j]) + " ref = " + str(xdata[i][0][j]))
      if ((xdata[i][-1][j] > (1+deviation)*xdata[i][0][j]) or (xdata[i][-1][j] < (1-deviation)*xdata[i][0][j])):
        print("Large deviation in the " + j + " of BPM" + str(i))
        print(" reference " + j + " " + str(xdata[i][0][j]))
        print(" current " + j + " " + str(xdata[i][-1][j]))

def check_MWPC():
  m = MWPC()
  v_intensity, h_intensity, fwhm_v, fwhm_h = m.get_data()
  print(v_intensity, h_intensity, fwhm_v, fwhm_h)
  return

def check_SEC():
  s = SEC()
  data = s.get_data()
  now = roundTime(datetime.now(), roundTo=60*60)
  try:
    last_spill = data.index[-1]
    warning = '{} - PROBLEM! NO BEAM SINCE {}!'.format(datetime.now(), last_spill)
  except IndexError:
    last_spill = datetime.strptime(t1, tf)
    warning = '{} - PROBLEM! NO BEAM FOR OVER 2 HOURS!'.format(datetime.now())
  d = (now-last_spill)
  if d.seconds>(45.0*60):
    print(warning)
    #alert('CHARM No Beam!', warning)
  else:
    print('{} - BEAM CHECK OK!'.format(now))
  return

check_BPM()
print("\n")
check_MWPC()
print("\n")
check_SEC()
