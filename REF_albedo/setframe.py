import albedo._albedo.timeseries as timeseries
#import _albedo.timeseries as timeseries
import param
from datetime import timedelta
import numpy as np

class SetFrame(timeseries.TimeSeries):
    
    @param.depends('date')
    def set_dataframe(self):
        self.dataframe = self.sun_position()
        filler = [0 for i in range(len(self.dataframe))]
        self.dataframe.insert(7, 'bin_assignment', filler)
        self.date_string = self.enabledDays[self.date].strftime("%Y-%m-%d")
        
        self.time_dict = {
            (t-timedelta(hours=self.UTC_offset)).strftime("%H:%M:%S"):index
            for index, t in enumerate(self.dataframe['UTC_datetime'])
        }
        
        self.param.time.objects = sorted(self.time_dict.values())
        self.param.time.names = self.time_dict
        return
    
    @param.depends('date', 'resolution', 'sigma', 'bins')
    def update_config(self):
        
        cell_scale = np.around(3/self.resolution, 5)
        self.geotransform = [0, cell_scale, 0, 0, 0, cell_scale]
        
        if self.bins != 'Max':
            bin_array       = np.linspace(0,360,self.bins,endpoint=True)
            real_azis       = self.dataframe['solarAzimuth'].to_numpy(copy=True)
            bin_assignment  = np.digitize(real_azis, bin_array)
            self.dataframe['bin_assignment'] = bin_assignment
            
            bin_angle = bin_array[1] # the angle width of a bin
            first_angle = bin_angle/2 
            last_angle = 360 - first_angle
            angle_array = np.linspace(first_angle, last_angle,
                                      self.bins-1, endpoint=True)
            self.angle_dict = dict(zip(np.arange(self.bins), angle_array))
            
        else:
            self.bin_dict = 'bins == Max: bin_dict not defined.'
        
        self.ID = (self.date_string.replace('-','')+'_'
                   +'R'+str(self.resolution)+'_'
                   +'S'+str(self.sigma).replace('.','')+'_'
                   +'B'+str(self.bins)
                  )
            
        self.dictionary = {
            'Constants': {
                'Easting Bounds': (self.eastMin, self.eastMax),
                'Northing Bounds': (self.northMin, self.northMax),
                'Projection': self.projection,
                'Vert Exag': self.vertEx,
                'UTC Offset': self.UTC_offset,
                'LatLong': (self.lat, self.long),
                'Time Series Resolution (min)': self.timeResolution,
                'Filepaths': {'Pointclouds': self.pointcloud_directory,
                              'Radiometers': self.rad_directory
                             }
            },
            'Configuration': {
                'Date': self.date_string,
                'Raster': {'Resolution': self.resolution,'Sigma': self.sigma},
                'Geotransform': self.geotransform,
                'Azimuth': {'Bins': [self.bins,
                                     (bin_array.tolist()
                                     if self.bins != 'Max' else 'N/A')]
                           }
            }
        }        
        return