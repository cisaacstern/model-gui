import param, os, datetime, itertools

class DataSet(param.Parameterized):
    
    #geographic constants
    eastMin, eastMax = 320977, 320980
    northMin, northMax = 4168144, 4168147        
    #geotransform = [0, 1, 0, 0, 0, 1]
    projection = 'WGS84'
    UTC_offset = 8
    lat, long = 37.643, -119.029
    
    #timeseries constants
    timeResolution = 15
    
    #TODO: transform constants. i.e. richdem vert. exagg.
    
    #filepath constants
    raw_directory = os.path.join(os.getcwd(), 'albedo', 'data', 'raw')
    
    pointcloud_directory = os.path.join(os.getcwd(), 'albedo', 'data', 'pointclouds')
    pointclouds = [file for file in os.listdir(pointcloud_directory)]
    pointclouds.sort()

    rad_directory = os.path.join(os.getcwd(), 'albedo', 'data', 'radiometers')
    radiometers = [file for file in os.listdir(rad_directory)]
    radiometers.sort()

    assert (len(pointclouds)==len(radiometers)), 'Fileset lengths unequal.'
    
    enabledDays = [datetime.datetime(
        int(filename[0:4]), int(filename[4:6]), int(filename[6:8]), 0, 0, 0, 0, 
        tzinfo=datetime.timezone.utc) for filename in pointclouds]
    
    #TODO: assert a check of enabled days against radiometer dates
    
    #for passing to Paramaters
    indexLength = len(pointclouds)-1 #this is probably not needed
    
    date_dict={date.strftime("%Y-%m-%d"):i for i,date in enumerate(enabledDays)}
    
    date = param.Selector(default=0, objects=date_dict)
    