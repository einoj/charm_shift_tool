from database_ctrl import *
from datetime import datetime

tf = '%Y-%m-%d %H:%M:%S'

dbc = db_commands()
dbc.respond(0)
dbc.respond(0)
response = dbc.get_response()
print(response==(0,))
