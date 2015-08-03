from database_ctrl import *
from datetime import datetime

tf = '%Y-%m-%d %H:%M:%S'

class Tester():

  def __init__(self):
    self.tests = 0
    self.errors = 0

  def testIfAsExpected(self, test, value, expected):
    if self.tests == 0:
      print()
      print("=================================================")
      print("== Starting testing.")
      print("=================================================")
    self.tests += 1
    if value == expected:
      result = str(value) + ", OK."
    else:
      self.errors += 1
      result = "ERROR, actual value " + str(value) + ", expected value: " + str(expected)
    print("== Testing " + test + ": " + result)  

  def print_stats(self):
    print()
    print("=================================================")
    print("== Ran " + str(self.tests) + " test(s).")
    print("== Encountered " + str(self.errors) + " error(s).")
    print("== " + str(100-self.errors/self.tests*100) + "% of the tests executed correctly.")


dbc = db_commands()
t = Tester()

# test shifter functions
shifter = ('Eino','eino.juhani.oltedal@cern.ch',4741760950,0)
dbc.insert_shifter(shifter)
shifter = ('Maris','maris.tali@cern.ch',9999999999,1)
dbc.insert_shifter(shifter)
t.testIfAsExpected('Set Shifter', dbc.get_current_shifter(), 'Maris')
dbc.set_current_shiter('Eino')
t.testIfAsExpected('Change Shifter', dbc.get_current_shifter(), 'Eino')
t.print_stats()
