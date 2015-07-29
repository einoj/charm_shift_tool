from data_retriver import BPM, MWPC, SEC
from datetime import datetime, timedelta
from database_ctrl import *
from email_tools import alert
from database_ctrl import db_commands
import time
import urllib

tf = '%Y-%m-%d %H:%M:%S'
calibration = {
    'SEC1': 2.2E7
}

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

def bpm_msg(data, axis):
  # BPMs are numbered 1 through 4
  # index 0 contains refrence data,
  # and the last index contains the most recent sampling
  db_cmd = db_commands()
  # divide by 100 because the database stores % not floats between 0 and 1
  deviation = db_cmd.get_setting('deviation')/100.
  del db_cmd
  check_centre = False
  check_fwhm = False
  msg = ""
  for d in data:
    j = 'fwhm'
    if ((d[-1][j] > (1+deviation)*d[0][j]) or (d[-1][j] < (1-deviation)*d[0][j])):
      msg += 'Large deviation in the ' + j + ' of ' + str(d[-1]['title']) + '\n'
      msg += ' reference ' + j + ' ' + str(d[0][j]) + '\n'
      msg += ' current ' + j + ' ' + str(d[-1][j]) + '\n'
      if (j == 'fwhm'):
        check_fwhm = True
    if  abs(d[-1]['centre'])  >= 4.5:
        msg += 'Off centre: ' + str(d[-1]['centre']) + " of " + str(d[-1]['title']) + '\n'
        check_centre = True #reference with the mwpc
  return msg, check_centre, check_fwhm

def check_BPM():
  b = BPM()
  xdata, ydata, bpm_error = b.get_bpm_data()
  xmsg, xcentre, xfwhm = bpm_msg(xdata, 'x-axis\n')
  ymsg, ycentre, yfwhm = bpm_msg(ydata, 'y-axis\n')
  return xmsg, ymsg, xcentre, xfwhm, ycentre, yfwhm, bpm_error

def check_MWPC():
  db_cmd = db_commands()
  ref_fv = db_cmd.get_setting('mwpc_V_FWHM')
  ref_fh = db_cmd.get_setting('mwpc_H_FWHM')
  ref_cv = db_cmd.get_setting('mwpc_V_center')
  ref_ch = db_cmd.get_setting('mwpc_H_centre')
  deviation = db_cmd.get_setting('deviation')/100.
  del db_cmd
  m = MWPC()
  fwhm_msg = ""
  centre_msg = ""
  fwhm_v, fwhm_h, centre_v, centre_h = m.get_data()
  print ("MWPC: fwhm v: " + str(fwhm_v) + " fwhm_h: " + str(fwhm_h) + " centre_v: " + str(centre_v) + " centre_h: " + str(centre_h))
  if abs(centre_v) > (1+deviation)*ref_cv:
    centre_msg += "MWPC vertical center offset: " + str(centre_v) + " mm\n"
  if abs(centre_h) > (1+deviation)*ref_ch:
    centre_msg += "MWPC horizontal center offset: " + str(centre_h) + " mm\n"
  if fwhm_v > (1+deviation)*ref_fv:
    fwhm_msg += "MWPC vertical FWHM too large: " + str(fwhm_v) + " mm\n"
  if fwhm_h > (1+deviation)*ref_fh:
    fwhm_msg += "MWPC horizontal FWHM too large: " + str(fwhm_h) + " mm\n"
  return centre_msg, fwhm_msg

def check_SEC():
  db_cmd = db_commands()
  deviation = db_cmd.get_setting('deviation')/100.
  del db_cmd
  s = SEC()
  data = s.get_data()
  reference = 3.5e11
  now = datetime.now()
  msg = ''
  warning = '{} - PROBLEM! NO BEAM!'.format(datetime.now())

  if type(data) == bool:
    # No recent sec data in timber
    return warning

  try:
    #check number of samples in last five minutes
    #there should be about 3.4 per minute
    #if it drops below 2.4 per minute, send a warning.
    #Do this because even if there has been no samples 
    #in the last five miutes, the intensity will still be high enough.
    fiveminago  = now - timedelta(minutes=5)
    samplecnt = 0
    timeindex = len(data.index)-1
    while (data.index[timeindex] > fiveminago):
      samplecnt += 1
      timeindex -= 1
    if (samplecnt < 10):
      return warning

    # Enough samples in the last 5 minutes, return intensity
    intensity = (data['pot/spill'].mean())
    last_spill = data.index[-1]
    print ("SEC intensity: " + str(intensity))
  except:
    return warning
  if ((intensity > (1+deviation)*reference) or (intensity < (1-deviation)*reference)):
    msg =  'SEC1 intesity: ' + str(intensity) + ' reference: ' + str(intensity)
  return msg

def running():

  while True:
    xmsg = ""
    ymsg = ""
    centre_msg = ""
    fwhm_msg = ""
    sec_msg = ""
    beam_status = 1
    centre_status = 1
    fwhm_status = 1
    subject = "Warning "
    warn_email = False
    warn_centre_email = False
    warn_fwhm_email = False

    #check only SEC for intensity
    sec_msg = check_SEC()
    if sec_msg != '':
      warn_email = True
      beam_status = 0
      centre_status = 0
      fwhm_status = 0
      subject += 'BEAM DOWN! '
    
    xmsg, ymsg, xcentre, xfwhm, ycentre, yfwhm, bpm_error = check_BPM()

    # Make sure the centre/fwhm is acutally off by also comparing to the SEC
    if (xfwhm or xcentre or ycentre or yfwhm or bpm_error):
      centre_msg, fwhm_msg = check_MWPC()
      if centre_msg != '':
        warn_centre_email = True
        subject += 'Beam off centre! '
      if fwhm_msg != '':
        warn_fwhm_email = True
        subject += 'Beam fwhm too wide '

    dbc = db_commands()
    last_msg = dbc.get_last_msg()
    t_now = (datetime.now()).strftime(tf)

    # Only send message if we haven't already
    whole_msg = 'SEC INFO\n----------------------------------------\n\n'+sec_msg+'\n\nBPM INFO\n----------------------------------------\n\nX-AXIS\n\n'\
    + xmsg + '\nY-AXIS\n\n' + ymsg + '\n\nMWPC INFO\n----------------------------------------\n\n'+centre_msg+fwhm_msg
    
    if last_msg is None:
        if warn_email or warn_fwhm_email or warn_centre_email:
            alert(subject, whole_msg, 'charm_shift_tool@cern.ch', 'eino.juhani.oltedal@cern.ch')
            dbc.insert_msg((t_now, whole_msg, 1*warn_email, 1*warn_fwhm_email, 1*warn_centre_email))
    else:
      if last_msg[-3] == 1:
        if warn_email:
        # If there is a warn_email, everything is down
            alert(subject, whole_msg, 'charm_shift_tool@cern.ch', 'eino.juhani.oltedal@cern.ch')
            dbc.insert_msg((t_now, whole_msg, 0, 0, 0))
        else:
            if (warn_fwhm_email and last_msg[-2] == 1) or (warn_centre_email and last_msg[-1] == 1):
                alert(subject, whole_msg, 'charm_shift_tool@cern.ch', 'eino.juhani.oltedal@cern.ch')
                dbc.insert_msg((t_now, whole_msg, 1, 1*warn_fwhm_email, 1*warn_centre_email))
            elif (warn_fwhm == False and last_msg[-2] == 0) and (warn_centre == False and last_msg[-1] == 0):
                alert('Notic Beam Centered and FWHM Normal', whole_msg, 'charm_shift_tool@cern.ch', 'eino.juhani.oltedal@cern.ch')
                dbc.insert_msg((t_now, whole_msg, 1, 1, 1))
      elif last_msg[-3] == 0 and warn_email == False:
          # Beam is now up again
          alert("Notice CHARM beam is up again", "Beam up again at " + t_now, 'charm_shift_tool@cern.ch', 'eino.juhani.oltedal@cern.ch')
          dbc.insert_msg((t_now, "Beam up again.", 1,1*warn_fwhm_email,1*warn_centre_email))
    del dbc
    print(whole_msg)
    time.sleep(600)

if __name__ == "__main__":
    running()
