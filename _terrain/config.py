import toml, os, datetime, itertools

#load config.toml
cwd = os.getcwd()
path = os.path.join(cwd, '_terrain', '_settings', 'config.toml')
config = toml.load(path)
#add config to locals
locals().update(config)
#...and a few more expressive variations
BOUNDS = [*EAST_BOUNDS, *NORTH_BOUNDS, *ELEV_BOUNDS]
EAST_MIN, EAST_MAX, NORTH_MIN, NORTH_MAX, ELEV_MIN, ELEV_MAX = BOUNDS

#create a list of topo data files
TOPO_PATH = os.path.join(cwd, 'data', 'topo')
TOPO_LIST = [file for file in os.listdir(TOPO_PATH)]
TOPO_LIST.sort()
#...and a list of timeseries data files
TIME_PATH = os.path.join(cwd, 'data', 'time')
TIME_LIST = [file for file in os.listdir(TIME_PATH)]
TIME_LIST.sort()
#assert that lengths of these two lists are equal
assert (len(TOPO_LIST)==len(TIME_LIST)), 'Fileset lengths unequal.'

#create list of datetime objects
ENABLED_DATES = [datetime.datetime(
    int(fn[0:4]), int(fn[4:6]), int(fn[6:8]), 0, 0, 0, 0, 
    tzinfo=datetime.timezone.utc) for fn in TOPO_LIST]
#...and iterable index of enabled datetimes
DATE_DICT={date.strftime("%Y-%m-%d"):i for i,date in enumerate(ENABLED_DATES)}