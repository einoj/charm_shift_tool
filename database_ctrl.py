# Functions for writing and readind to the charm shift database.
# The data base contains three different tables, one for user settings
# one containing reference values for the beam position detectors, and
# one for the beam intensity detectors.
# There are three user settings inserted into the settings table.
# They are:
# 1. Amout of time the beam is down before a message is sent in minutes,
# 2. Percentage increase/decrease in the intesity from the reference before a message is sent.
# 3. Percentage increase/decrease in the doserate per hour before a message is sent.

import sqlite3

database  = 'charm_shift.db'
set_table = 'settings'
pos_table = 'BPMs_and_MWPC'
int_table = 'Intensity_detectors'

default_pos = []

class db_commands:
    def __init__(self):
        '''
        Here I'm not sure if it's better to leave the database open and close manually after, or do
        as you are now and open and close within each function. Either way would work, and I guess
        closing it after each call is cleaner and potentially safer.
        :return:
        '''
        self.load_db()
        # Make sure that tables exist
        self.cur.execute('create table if not exists ' + set_table + ' (id int, name text, setting int)')
        self.cur.execute('create table if not exists ' + pos_table + ' (id int, name text, x_intensity float, x_fwhm float, y_intesity float, y_fwhm float)')
        self.cur.execute('create table if not exists ' + int_table + ' (id int, name text, intensity float)')
        self.con.commit()
        self.close_db()

    def __del__(self):
      self._db_connection.close()
        
    def load_db(self):
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()
    
    def close_db(self):
      self.con.close()
    #def init_tables(self):
        # init settings table

    def insert_setting(self, data):
      if len(data) != 3:
        print("ERROR: A row in settings has 3 columns, not " + str(len(data)) + "!")
        return
      self.load_db()
      self.cur.execute("insert into " + set_table + " values(?,?,?)", data)
      self.con.commit()
      self.close_db()

    def insert_int_detector(self, data):
      if len(data) != 6:
        print("ERROR: A row in settings has 3 columns, not " + str(len(data)) + "!")
        return
      self.load_db()
      self.cur.execute("insert into " + int_table + " values(?,?,?)", data)
      self.con.commit()
      self.close_db()

    def insert_pos_detector(self, data):
      if len(data) != 3:
        print("ERROR: A row in settings has 3 columns, not " + str(len(data)) + "!")
        return
      self.load_db()
      self.cur.execute("insert into " + pos_table + " values(?,?,?)", data)
      self.con.commit()
      self.close_db()

    def print_tables(self):
      self.load_db()
      self.cur.execute("select * from settings")
      data = self.cur.fetchall()
      for d in data:
        print(d)
      self.close_db()

    def remove_all(self):
      self.load_db()
      self.cur.execute("delete from " + set_table)
      self.cur.execute("delete from " + pos_table)
      self.cur.execute("delete from " + int_table)
      self.con.commit()
      self.close_db()
        
    #cur.execute("insert into " + set_table + " values(1,'timer',10)")
    #con.commit()
