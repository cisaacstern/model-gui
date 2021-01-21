'''
Provides the classes TimeSeries and Correction.
'''
import datetime
import numpy as np
import pandas as pd
from pysolar import solar
import terrain.config as c

class TimeSeries():
    '''
    This class initializes a dataframe.
    It also provides static methods for _ and _.
    '''
    def __init__(self, date):
        self.date = date
        self.df = self.initialize_dataframe()

    def initialize_dataframe(self):
        '''
        This is an instance method which serves as a helper for __init__.
        '''
        def load_csv(date):
            '''
            Loads a dataframe of radiometer data for the specified date
            '''
            return pd.read_csv(c.TIME_PATH + '/' + c.TIME_LIST[date])
    
        def drop_ncols_nrows(df):
            '''
            drops unnecessary columns and non-sunlit rows from the dataframe,
            reduces time resolution of dataframe by removing rows based on the
            provided timeInterval. (e.g. timeInterval=15 reduces time resolution
            of dataframe to 15 min intervals).
            '''
            df = df.drop(df.columns[[1,2,3,5,6,7,8,9,12]],axis=1) #dropping unnecessary columns
            df = df.iloc[::c.TIME_RESOLUTION] #reduce time resolution
            col='upward looking solar radiation; uplooking Sunshine pyranometer  direct and diffuse; (Watts/meter^2)'
            return df[df[col] > 1.5]  #dropping non-sunlit rows from top and bottom (first pass)

        def add_utc(df):
            '''
            Adds utc datetime to dataframe. This is necessary for running 
            sun position with `pysolar.solar`.
            '''
            utc_list = []
            for i in range(0,df.shape[0]):
                time_str = df.iloc[i,0] 
                year, month = int(time_str[0:4]), int(time_str[5:7])
                day = int(time_str[8:10])
                hour = int(time_str[11:13])+c.UTC_OFFSET
                minute = int(time_str[14:16])

                if hour < 24:
                    day = day
                elif hour >= 24:
                    day = day+1
                    hour = hour-24

                dt = datetime.datetime(year, month, day, hour, minute, 0, 0, tzinfo=datetime.timezone.utc)
                utc_list.append(dt)
            
            df.insert(1, 'utc_datetime', utc_list)
            return df
    
        def add_sun_position(df):
            '''
            solar altitude + azimuth to dataframe, makes a second pass as dropping 
            non-sunlit timepoints by removing rows for which solar altitude is < 0.
            '''
            _lat, _long = c.LAT_LONG
            alt_list = [90 - solar.get_altitude(_lat, _long, utc_time) 
                        for utc_time in df['utc_datetime']]
            azi_list = [solar.get_azimuth(_lat, _long, utc_time) 
                        for utc_time in df['utc_datetime']]

            df.insert(5, 'solar_altitude', alt_list)
            df.insert(6, 'solar_azimuth', azi_list)

            return df[df['solar_altitude'] < 90]  #dropping non-sunlit rows from top and bottom (second pass)

        def add_bin_placeholder(df):
            placeholder = [0 for i in range(len(df))]
            df.insert(7, 'bin_assignment', placeholder)
            return df
        
        df = load_csv(self.date)
        df = drop_ncols_nrows(df=df)
        df = add_utc(df=df)
        df = add_sun_position(df=df)
        df = add_bin_placeholder(df=df)
        return df

    @staticmethod
    def reassign_bins(bins, df):
        '''
        Reassigns azimuth binning in a timeseries dataframe 
        based on the given number of bins.
        '''
        bin_array = np.linspace(0, 360, num=bins, endpoint=True)
        real_azis = df['solar_azimuth'].to_numpy(copy=True)
        bin_assgn = np.digitize(real_azis, bins=bin_array)
        df['bin_assignment'] = bin_assgn
        return df

    @staticmethod
    def generate_angle_dict(bins):
        '''
        Generates a mapping of bins to azimuth angles.
        The resulting dictionary is used for plotting sun position.
        '''
        bin_arr  = np.linspace(0, 360, num=bins, endpoint=True)
        ang_wdth = bin_arr[1] # the "angular width" of a bin
        frst_ang = ang_wdth/2 
        last_ang = 360 - frst_ang
        ang_arr  = np.linspace(frst_ang, last_ang, bins-1, endpoint=True)
        ang_dict = dict(zip(np.arange(bins), ang_arr))
        return ang_dict


class Correction():
    '''
    This class provides static methods for corrections.
    '''
    @staticmethod
    def calculate_correction(grids, df, time, planar=False):
        '''
        The argument `grids` should be a tuple of `length = 2` for which
        `grids[0]` is an array of slope values in radians, and grids[1]
        is an array of aspect values in degrees, with south = 0, and east positive.

        '''
        alt = df['solar_altitude'].iloc[time]
        azi = df['solar_azimuth'].iloc[time]
    
        if planar==True:
            #slope, aspect = self.p_slope, self.p_aspect
            pass
        else:
            slope, aspect = grids

        T0 = np.deg2rad(alt)
        P0 = np.deg2rad(180 - azi)

        S = np.deg2rad(slope) 
        A = np.deg2rad(aspect)

        cosT0 = np.cos(T0)
        cosS = np.cos(S)
        sinT0 = np.sin(T0)
        sinS = np.sin(S)
        cosP0A = np.cos(P0 - A)

        cosT = (cosT0*cosS) + (sinT0*sinS*cosP0A)

        return cosT/cosT0
