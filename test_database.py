from database_ctrl import *
from datetime import datetime

tf = '%Y-%m-%d %H:%M:%S'

dbc = db_commands()
#dbc.insert_setting((1, 'time', 10))
#dbc.insert_setting((1, 'bpm1', 10.1, 2.34,12.2,4.0))
t_now = (datetime.now()).strftime(tf)
dbc.insert_msg((t_now, "Test message sfjasgjasgakvn;lak ads sakjfsak jfsakj lsdjf skajf sakj f;lksaj:231414 51", 1))
dbmsg = dbc.get_last_msg()
print(type(dbmsg[-1]))
#dbc.print_tables()
dbc.remove_all()
del dbc
#dbc.print_tables()

