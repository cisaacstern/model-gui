import numpy as np

class Correction():
    '''
    This class provides a single static method.
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
