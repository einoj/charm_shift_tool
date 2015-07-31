from database_ctrl import *
from datetime import datetime

tf = '%Y-%m-%d %H:%M:%S'

dbc = db_commands()
dbc.insert_shifter('Ruben')
print(dbc.get_shifter())
