import logging
import numpy as np
from scipy import ndimage

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

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


class Horizon():
    '''
    This class initializes horizons in the "ill posed manner" described in Dozier.
    Once initialized, it provides instance methods for calculating shade at selected timepoints.
    In reality, each sun position has a unique azimuth. For the purposes of this model, however,
    we bin azimuth into a discrete number of user-defined buckets. This explains why we
    initalize this class based on the azimuth: because azimuths are reused for multiple timepoints
    i.e. altitudes. Azimuths are also the most computationally expensive.
    '''
    def __init__(self, df, azimuth, elev_grid):
        '''

        '''
        self.df = df
        self.azimuth = azimuth
        self.rotated_elevation_grid, self.rotated_slope_array = (
            self._initialize_azimuth(azimuth=azimuth, elev_grid=elev_grid)
        )

    #---------------------------------------------------------------------
    # Private API
    #---------------------------------------------------------------------

    @staticmethod
    def _initialize_azimuth(azimuth, elev_grid):
        '''
        This is an static method which serves as a helper for __init__.
        It is static bc somehow I think that'll make it easier to @jit it.
        '''
        logger.debug('Hello you\'re in the initalizer')

        def _rotate2azimuth(azimuth, elev_grid):
            '''
            rotates a grid so that North is re-referenced to be
            facing the solar azimuth. See Dozier page XX fig XX.
            '''
            logger.debug('Step 1: you\'re in the rotater')

            return ndimage.rotate(input=elev_grid, angle=(-azimuth),
                    reshape=True, order=0, mode='constant', cval=np.nan)
        
        def _slope(g, i, j, k):
            '''
            g is the elevation grid, i and j are row indicies, k is the column index
            '''
            if g[j, k] >= g[i, k]:
                return (g[j, k] - g[i, k])/(j-i)
            else:
                return 0
        
        def _calc_horizon_indices(grid):
            '''
            the horzPt for a given elevG[i, k] is expressed as an index value of elevG[]
            '''

            horz_arr = np.zeros(grid.shape, dtype=int)
            nhorz = horz_arr.shape[0]

            logger.debug(f'Step 2: you\'re in the indexer, nhorz = {nhorz}')

            for k in range(0, nhorz-1):
                                
                horz_arr[nhorz-1, k] = nhorz - 1 #the first entry is its own horizon

                for i in range(nhorz-2, -1, -1): #loop from next-to-end backward to beginning
                    
                    j = i + 1
                    horzj = horz_arr[j, k]
                    i_to_j = _slope(grid, i=i, j=j, k=k)
                    i_to_horzj = _slope(grid, i=i, j=horzj, k=k)

                    while i_to_j < i_to_horzj:
                        j = horzj
                        horzj = horz_arr[j, k]
                        i_to_j = _slope(grid, i=i, j=j, k=k)
                        i_to_horzj = _slope(grid, i=i, j=horzj, k=k)

                    if i_to_j > i_to_horzj:
                        horz_arr[i, k] = j
                    elif i_to_j == 0:
                        horz_arr[i, k] = i
                    else:
                        horz_arr[i, k] = horzj

            return horz_arr

        def _calc_horizon_slope(grid, horz_arr, scale=0.01):
            '''
            takes a rotated elevation grid and a corresponding horzPt array,
            from self.fwdHorz2D, and calculates the slope from each point on
            the elevation grid to its horizon point in the horzPt array.
            returns the elevation grid and a 'slope to horizon (radians)' array
            '''
            logger.warning('Step 3: you\'re in the sloper. WHAT IS SCALE?')

            shape = grid.shape
            slope_arr = np.zeros(shape)

            for k in range(0, shape[0]):
                for i in range(0, shape[0]):
                    slope_arr[i,k] = (
                        np.arctan2(
                            grid[horz_arr[i,k], k] - grid[i,k],
                            ((scale * horz_arr[i,k]) - (scale * i))
                        )
                    )
            return slope_arr
        
        rotated_grid = _rotate2azimuth(azimuth, elev_grid)
        horizon_indices = _calc_horizon_indices(grid=rotated_grid)
        rotated_slope_array = (
            _calc_horizon_slope(rotated_grid, horz_arr=horizon_indices)
        )

        return rotated_grid, rotated_slope_array    

    #---------------------------------------------------------------------
    # Public API
    #---------------------------------------------------------------------

    @staticmethod
    def calc_obstruction_for_altitude(altitude, azimuth, rot_elev, rot_slope, 
                                        resolution):
        '''

        '''
        def _calc_rotated_mask(alt, rot_slope):
            '''
            takes an elevation array, a 'slope to horizon (radians)' array,
            and a solar altitude as inputs, returns a (TILTED) array of visible points
            '''
            #assert alt 
            alt = np.deg2rad(90 - alt)
            shape = rot_slope.shape
            mask = np.zeros(shape)
            for k in range(0, shape[0]):
                for i in range(0, shape[0]):
                    if rot_slope[i,k] > alt:
                        mask[i,k] = 1
                    elif rot_slope[i,k] < alt:
                        mask[i,k] = 0
                    else:
                        mask[i,k] = -1
                    
            return mask
    
        def _bbox(array):
            '''
            A helper for the _rerotate_mask method.
            '''
            rows = np.any(array, axis=1)
            cols = np.any(array, axis=0)
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]

            return rmin, rmax, cmin, cmax

        def _rerotate_mask(rot_elev, rot_mask, azi):   
            '''
            rotate mask back to original position, set non-1s to zeros
            '''
            
            #rotated_elevG, tiltedMask = self.invisiblePoints()
            #dimLength = self.resolution
            
            mask = ndimage.rotate(rot_mask, angle=azi, reshape=True, 
                                    order=0, mode='constant', cval=np.nan)

            mask[np.isnan(mask)] = 0
            mask[mask == 0.5] = 0

            #create ref from the rotated elevation grid, set nans to zeros, extract extents from ref
            ref = ndimage.rotate(rot_elev, angle=azi, reshape=True, 
                                    order=0, mode='constant', cval=np.nan)
            ref[np.isnan(ref)] = 0
            rmin, rmax, cmin, cmax = _bbox(array=ref)

            #clip extractMask using referenced extents, reset extractMask 0's to nan's
            mask = mask[rmin:rmax, rmin:cmax]
            mask[mask==0] = np.nan

            return mask
    
        def _square_mask(mask, resolution):
            '''

            '''
            target_shape = (resolution, resolution)

            if mask.shape == target_shape:
                mask = mask
            elif mask.shape != target_shape:
                row_diff = target_shape[0] - mask.shape[0]
                col_diff = target_shape[1] - mask.shape[1]
                row_stacker = np.zeros((mask.shape[0]))
                col_stacker = np.zeros((target_shape[1],1))

                if mask.shape[0] == mask.shape[1]:
                    for i in range(1,row_diff+1):
                        mask = np.append(mask, [row_stacker], axis=0)
                    for i in range(1,col_diff+1):
                        mask = np.append(mask, col_stacker, axis=1)
                else:
                    mask = np.zeros(target_shape)
                
            mask[mask==0] = np.nan

            return mask
        
        rotated_mask = _calc_rotated_mask(alt=altitude, rot_slope=rot_slope)
        rerotated_mask = _rerotate_mask(
            rot_elev=rot_elev, rot_mask=rotated_mask, azi=azimuth
        )
        square_mask = _square_mask(mask=rerotated_mask, resolution=resolution)

        return square_mask

    #---------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------- 
