#from .automated_simulation import *
from .nyiso_data import *
from .pf2rec import *
#from .pf_automation import *


PREV_NOW = datetime.datetime.now() + datetime.timedelta(days = -1)
CURRENT_DATE = f"{PREV_NOW.month:02d}/{PREV_NOW.day:02d}/{PREV_NOW.year}"
CURRENT_YEAR = datetime.datetime.now().year

HELP_FUNCTION = "Function to perform: `nyiso` for downloading NYISO data, `run_pf` to download time-series power flow with NYISO data, `run_sim` to run time-domain simulations using different power flows"

HELP_YEAR = "(`nyiso`) Year from which the NYISO data download begins (defaults to current year)"
HELP_PATH = "(`nyiso`) Path for the files downloaded from NYISO. Defaults to './data'"

HELP_VERSION = "(`run_pf` and `run_sim`) OpenIPSL version to generate the time-series power flows. Defaults to '1.5.0'"
HELP_WINDOW = "(`run_pf`) Length of the time window to run the power flow computation ('day', 'week', 'month'). Defaults to 'day'"
HELP_DATE = "(`run_pf`) Date to run the power flow. Must be passed in mm/dd/YYYY format for 'day' and 'week' (it can be any day of the week), and 'mm/YYYY' for month. 'Defaults to current day - 1'"
HELP_LOADS = "(`run_pf`) Number of loads to change according to the time series data. Defaults to 'all'"

HELP_TOOL = "(`run_sim`) Tool to run time-domain simulations. 'OM' for OpenModelica and 'dymola' for Dymola. Defaults to 'dymola'"

NYISO_ZONES = ['CAPITL', 'CENTRL', 'DUNWOD', 'GENESE', 'HUD VL', 'LONGIL', 'MHK VL', 'MILLWD', 'N.Y.C.', 'NORTH', 'WEST', 'NYISO']
