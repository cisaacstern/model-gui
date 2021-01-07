import param, os, datetime, itertools

class DataSet(param.Parameterized):
    
    #geographic constants
    EAST_MIN, EAST_MAX = 320977, 320980
    NORTH_MIN, NORTH_MAX = 4168144, 4168147
    ELEV_MIN, ELEV_MAX = 2941.977, 2948.356

    PROJECTION = 'WGS84'
    UTC_OFFSET = 8
    LAT, LONG = 37.643, -119.029
    
    #timeseries constants
    TIME_RESOLUTION = 15
        
    #filepath constants    
    LIDAR_PATH = os.path.join(os.getcwd(), 'data', 'pointclouds')
    LIDAR_LIST = [file for file in os.listdir(pointcloud_directory)]
    LIDAR_LIST.sort()

    RADIOMETER_PATH = os.path.join(os.getcwd(), 'data', 'radiometers')
    RADIOMETER_LIST = [file for file in os.listdir(rad_directory)]
    RADIOMETER_LIST.sort()

    assert (len(pointclouds)==len(radiometers)), 'Fileset lengths unequal.'
    
    ENABLED_DATES = [datetime.datetime(
        int(filename[0:4]), int(filename[4:6]), int(filename[6:8]), 0, 0, 0, 0, 
        tzinfo=datetime.timezone.utc) for filename in LIDAR_LIST]
        
    #for passing to Paramaters    
    DATE_DICT={date.strftime("%Y-%m-%d"):i for i,date in enumerate(ENABLED_DATES)}
    
    date = param.Selector(default=0, objects=DATE_DICT)
    