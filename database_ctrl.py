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

database  = '//cern.ch/dfs/Websites/t/test-charmShiftTool/data/charm_shift.db'
set_table = 'settings'
user_table = 'User_info'
msg_table = 'messages'
#status_table 'status'
response_table = 'response'
shifter_table = 'shifter'

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
        self.cur.execute('create table if not exists ' + set_table + ' (id INTEGER PRIMARY KEY, name text, setting int)')
        self.cur.execute('create table if not exists ' + user_table + ' (id INTEGER PRIMARY KEY, name text, email text, phone int)')
        self.cur.execute('create table if not exists ' + msg_table + ' (id INTEGER PRIMARY KEY, time text, msg text, status int, fwhm int, centre int)')
        #self.cur.execute('create table if not exists ' + status_table + ' (id INTEGER PRIMARY KEY, text, msg text, status int)')
        self.cur.execute('create table if not exists ' + response_table + ' (id INTEGER PRIMARY KEY, name text, status int)')
        self.cur.execute('create table if not exists ' + shifter_table + ' (id INTEGER , name text)')
        self.con.commit()
        self.close_db()

    #def __del__(self):
    #  self._db_connection.close()
        
    def load_db(self):
        self.con = sqlite3.connect(database)
        self.cur = self.con.cursor()
    
    def close_db(self):
      self.con.close()

    def insert_user(self, data):
      if len(data) != 4:
        print("ERROR: A row in settings has 4 columns, not " + str(len(data)) + "!")
        return -1
      self.load_db()
      self.cur.execute("insert into " + user_table + " values(?,?,?)", data)
      self.con.commit()
      self.close_db()

    def insert_setting(self, data):
      if len(data) != 2:
        print("ERROR: A row in settings has 2 columns, not " + str(len(data)) + "!")
        return -1
      self.load_db()
      # Insert new setting if one with the same name does not exist
      # else update the setting
      # I am unsure if this is the best way of doing it 
      # Using insert or ingore might be a better method
      self.cur.execute("select rowid from settings where name = ?",(data[0],))
      row = self.cur.fetchone()
      if row is None:
        self.cur.execute("insert into " + set_table + "(name, setting)" " values(?,?)", data)
      else:
        self.cur.execute("update settings set setting=? where name=?",(data[1],data[0]))
      self.con.commit()
      self.close_db()

    def insert_shifter(self, name):
      if type(name) != str:
        print("ERROR: Shifter name must be a string !")
        return -1
      self.load_db()
      self.cur.execute("select * from shifter")
      row = self.cur.fetchone()
      if row is None:
        self.cur.execute("insert into " + shifter_table + "(id, name) values("  +str(1) +",'"+name+"')")
      else:
        self.cur.execute("update shifter set name='" + name +"' where id=1")
      self.con.commit()
      self.close_db()

    def get_shifter(self):
      self.load_db()
      self.cur.execute("select name from " + shifter_table)
      shifter = self.cur.fetchone()
      if shifter != None:
        shifter = shifter[0]
      return shifter

    def get_setting(self, settingname):
      if type(settingname) != str:
        print("ERROR: must supply setting name as a string")
        return -1
      self.load_db()
      self.cur.execute("select * from settings where name='"+settingname+"'")
      setting = self.cur.fetchone()
      setting = int(setting[2])
      return setting

    def insert_msg(self, data):
      if len(data) != 5:
        print("ERROR: A row in settings has 5 columns, not " + str(len(data)) + "!")
        return -1
      self.load_db()
      #data = [self.cur.lastrowid()+1]+data
      self.cur.execute("insert into " + msg_table + "(time,msg,status,fwhm,centre)" " values(?,?,?,?,?)", data)
      self.con.commit()
      self.close_db()

    def get_last_msg(self):
      self.load_db()
      self.cur.execute("select * from "+msg_table+" where id=(select max(id) from " + msg_table+")")
      msg = self.cur.fetchone() 
      self.close_db()
      return msg

    def get_last_x_msgs(self, x):
      self.load_db()
      self.cur.execute("select * from "+msg_table+" order by id DESC limit " + str(x))
      msg = self.cur.fetchall() 
      self.close_db()
      return msg

    def get_beam_status(self):
      self.load_db()
      self.cur.execute("select * from "+msg_table+" where id=(select max(id) from " + msg_table+")")
      msg = self.cur.fetchone() 
      beam = msg[3]
      fwhm = msg[4]
      centre = msg[5]
      return beam, fwhm, centre

    def get_response(self):
      self.load_db()
      self.cur.execute("select status from "+response_table+" where name='beam'")
      beam = self.cur.fetchone()
      # Will return None if there is no response in database
      return beam

    def respond(self, x):
      if type(x) != int:
        print("ERROR: first argument must be a string and second argument an int")
        return -1
      self.load_db()
      self.cur.execute("select rowid from "+response_table+" where name='beam'")
      data = ('beam',x)
      row = self.cur.fetchone()
      if row is None:
        self.cur.execute("insert into " + response_table + "(name, status)" " values(?,?)", data)
      else:
        self.cur.execute("update "+response_table+" set status=? where name='beam'",(x,))
      self.con.commit()
      self.close_db()

    def print_tables(self):
      self.load_db()
      self.cur.execute("select * from messages")
      data = self.cur.fetchall()
      for d in data:
        print(d)
      self.close_db()

    def remove_all(self):
      self.load_db()
      self.cur.execute("delete from " + set_table)
      self.cur.execute("delete from " + msg_table)
      self.cur.execute("delete from " + user_table)
      self.con.commit()
      self.close_db()
