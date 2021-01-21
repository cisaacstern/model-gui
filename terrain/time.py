'''
Provides the classes TimeSeries, Correction, and Horizon.
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
        self.df = self._initialize_dataframe()

    #---------------------------------------------------------------------
    # Private API
    #---------------------------------------------------------------------

    def _initialize_dataframe(self):
        '''
        This is an instance method which serves as a helper for __init__.
        '''
        df = self._load_csv(self.date)
        df = self._drop_ncols_nrows(df=df)
        df = self._add_utc(df=df)
        df = self._add_sun_position(df=df)
        df = self._add_bin_placeholder(df=df)
        return df

    @staticmethod
    def _load_csv(date):
        '''
        Loads a dataframe of radiometer data for the specified date
        '''
        return pd.read_csv(c.TIME_PATH + '/' + c.TIME_LIST[date])

    @staticmethod
    def _drop_ncols_nrows(df):
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

    @staticmethod
    def _add_utc(df):
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

    @staticmethod
    def _add_sun_position(df):
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

    @staticmethod
    def _add_bin_placeholder(df):
        placeholder = [0 for i in range(len(df))]
        df.insert(7, 'bin_assignment', placeholder)
        return df

    #---------------------------------------------------------------------
    # Public API
    #---------------------------------------------------------------------

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
