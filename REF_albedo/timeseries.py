import albedo._albedo.griddata as griddata
#import _albedo.griddata as griddata
import pandas as pd
import datetime
from pysolar import solar
import numpy as np

class TimeSeries(griddata.GridData):
    
    def return_dataframe(self):
        '''
        loads a dataframe of radiometer data for the specified date
        '''
        return pd.read_csv(self.rad_directory + '/' + self.radiometers[self.date])
    
    def drop_ncols_nrows(self):
        '''
        drops unnecessary columns and non-sunlit rows from the dataframe,
        reduces time resolution of dataframe by removing rows based on the
        provided timeInterval. (e.g. timeInterval=15 reduces time resolution
        of dataframe to 15 min intervals).
        '''
        df = self.return_dataframe()
        df = df.drop(df.columns[[1,2,3,5,6,7,8,9,12]],axis=1) #dropping unnecessary columns
        df = df.iloc[::self.timeResolution] #reduce time resolution
        col='upward looking solar radiation; uplooking Sunshine pyranometer  direct and diffuse; (Watts/meter^2)'
        return df[df[col] > 1.5]  #dropping non-sunlit rows from top and bottom (first pass)

    def timestamp2UTC(self):
        '''
        adds UTC_datetime to dataframe.
        '''
        df, UTC_list = self.drop_ncols_nrows(), []
        for i in range(0,df.shape[0]):
            timeString = df.iloc[i,0]
            year, month = int(timeString[0:4]), int(timeString[5:7])
            day = int(timeString[8:10])
            hour = int(timeString[11:13])+self.UTC_offset
            minute = int(timeString[14:16])
            
            if hour < 24:
                day = day
            elif hour >= 24:
                day = day+1
                hour = hour-24
            else:
                print('time error')
            
            dt = datetime.datetime(year, month, day, hour, minute, 0, 0, tzinfo=datetime.timezone.utc)
            
            UTC_list.append(dt)
        
        df.insert(1, 'UTC_datetime', UTC_list)
        
        return df
    
    def sun_position(self):
        '''
        solar altitude + azimuth to dataframe,
        makes a second pass as dropping non-sunlit timepoints by removing
        rows for which solar altitude is < 0.
        '''
        df = self.timestamp2UTC()
        
        alt_list = [90 - solar.get_altitude(self.lat, self.long, utc_time) 
                    for utc_time in df['UTC_datetime']]
        
        azi_list = [solar.get_azimuth(self.lat, self.long, utc_time) 
                    for utc_time in df['UTC_datetime']]
    
        df.insert(5, 'solarAltitude', alt_list)
        df.insert(6, 'solarAzimuth', azi_list)

        return df[df['solarAltitude'] < 90]  #dropping non-sunlit rows from top and bottom (second pass)
    
    def M_calculation(self, df, row, choice):
        '''
        '''
        solAlt = df['solarAltitude'].iloc[row]
        solAzi = df['solarAzimuth'].iloc[row]
    
        if choice == 'planar':
            slope, aspect = self.p_slope, self.p_aspect
        elif choice == 'raster':
            slope, aspect = self.slopeRast, self.aspectRast
        elif choice == 'masked':
            slope, aspect = self.masked_slope, self.masked_aspect

        T0 = np.deg2rad(solAlt)
        P0 = np.deg2rad(180 - solAzi)

        S = np.deg2rad(slope) 
        A = np.deg2rad(aspect)

        cosT0 = np.cos(T0)
        cosS = np.cos(S)
        sinT0 = np.sin(T0)
        sinS = np.sin(S)
        cosP0A = np.cos(P0 - A)

        cosT = (cosT0*cosS) + (sinT0*sinS*cosP0A)

        return cosT/cosT0
    