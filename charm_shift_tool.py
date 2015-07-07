from data_retriver import BPM, MWPC


deviation = .3

def check_BPM():
  # BPMs are numbered 1 through 4
  # index 0 contains refrence data,
  # and the last index contains the most recent sampling
  b = BPM()
  ret_str  = ""
  xdata, ydata = b.get_bpm_data()
  for i in range(len(xdata)):
    for j in  ('intensity','fwhm'):
      if ((xdata[-1][j] > (1+deviation)*xdata[0][j]) or (xdata[-1][j] < (1-deviation)*xdata[0][j])):
        print("Large deviation in the " + j + " of BPM" + str(i))
        print(" reference " + j + " " + str(xdata[0][j]))
        print(" current " + j + " " + str(xdata[-1][j]))

def check_MWPC():
  m = MWPC()
  msg1, msg2 = m.fetch_from_timber()
  print(msg1, msg2)
  return

def check_SEC():
  return

check_BPM()
print("\n")
check_MWPC()
