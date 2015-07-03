from database_ctrl import *

dbc = db_commands()
dbc.insert_setting((1, 'time', 10))
dbc.insert_setting((1, 'bpm1', 10.1, 2.34,12.2,4.0))
dbc.print_tables()
dbc.remove_all()
dbc.print_tables()

from data_retriver import *
get_bpm_data()
