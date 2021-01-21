import numpy as np
from scipy import ndimage


class Horizon():
    '''
    This class initializes horizons in the "ill posed manner" described in Dozier.
    Once initialized, it provides instance methods for calculating shade at selected timepoints.
    In reality, each sun position has a unique azimuth. For the purposes of this model, however,
    we bin azimuth into a discrete number of user-defined buckets. This explains why we
    initalize this class based on the azimuth: because azimuths are reused for multiple timepoints
    i.e. altitudes. Azimuths are also the most computationally expensive.
    '''
    def __init__(self, df, elev_grid, angle_dict, _bin):
        '''

        '''
        #self.df = df
        self.azimuth = angle_dict[_bin]
        self.rotated_grid, self.slope_array = self.initialize_horizons(
            angle_dict=angle_dict, _bin=_bin, elev_grid=elev_grid
        )

    @staticmethod
    def _initialize_horizons(azimuth, elev_grid):
        '''
        This is an static method which serves as a helper for __init__.
        It is static bc somehow I think that'll make it easier to @jit it.
        '''
        rotated_grid = _rotate2azimuth(df, angle_dict, time, elev_grid)
        horizon_indices = _calc_horizon_indices(grid=rotated_grid)
        slope_array = _calc_horizon_slope(rotated_grid, horz_arr=horizon_indices)

        return rotated_grid, slope_array
    
    @staticmethod
    def _rotate2azimuth(azimuth, elev_grid):
        '''
        rotates an elevation raster so that North is re-referenced to be
        facing the solar azimuth. See Dozier page XX fig XX.
        '''
        #col = df['bin_assignment']
        #azimuth = angle_dict[col.iloc[time]]
        #azimuth = angle_dict[_bin]
            
        rot_grid = ndimage.rotate(input=elev_grid, angle=(-azimuth),
                                    reshape=True, order=0, 
                                    mode='constant', cval=np.nan)

        return rot_grid

    @staticmethod
    def _slope(g, i, j, k):
        '''
        g is the elevation grid, i and j are row indicies, k is the column index
        '''
        if g[j, k] >= g[i, k]:
            return (g[j, k] - g[i, k])/(j-i)
        else:
            return 0

    @staticmethod  
    def _calc_horizon_indices(grid):
        '''
        elevG is the blurred *AND ROTATED* elevation grid. horzPt[] is an empty
        *2D array* to be filled with the horzPts for each cell in THE ROTATED elevation grid
        the horzPt for a given elevG[i, k] is expressed as an index value of elevG[]
        '''
        horz_arr = np.zeros(grid.shape, dtype=int)
        nhorz = horz_arr.shape[0]

        for k in range(0, nhorz-1):
            horz_array[nhorz-1, k] = nhorz - 1 #the first entry is its own horizon
            
            for i in range(nhorz-2, -1, -1): #loop from next-to-end backward to beginning
                j = i + 1
                horzj = horz_arr[j, k]
                i_to_j = _slope(grid, i=i, j=j, k=k)
                i_to_horzj = _slope(grid, i=i, j=horzj, k=k)

                while i_to_j < i_to_horzj:
                    j = horz_j
                    horzj = horz_arr[j, k]
                    slope_i_to_j = _slope(grid, i=i, j=j, k=k)
                    slope_i_to_horz_j = _slope(grid, i=i, j=horzj, k=k)

                if i_to_j > i_to_horzj:
                    horz_arr[i, k] = j
                elif i_to_j == 0:
                    horz_arr[i, k] = i
                else:
                    horz_arr[i, k] = horzj

        return horz_arr
        
    @staticmethod  
    def _calc_horizon_slope(grid, horz_arr, scale=0.01):
        '''
        takes a rotated elevation grid and a corresponding horzPt array,
        from self.fwdHorz2D, and calculates the slope from each point on
        the elevation grid to its horizon point in the horzPt array.
        returns the elevation grid and a 'slope to horizon (radians)' array
        '''
        shape = grid.shape
        slope_arr = np.zeros(shape)

        for k in range(0, shape[0]):
            for i in range(0, shape[0]):
                slope_arr[i,k] = np.arctan2(
                                    x1 = grid[horz_arr[i,k], k] - grid[i,k],
                                    x2 = ((scale * horz_arr[i,k]) - (scale * i))
                                )
        return slope_arr

    @staticmethod
    def _obscured_points(self, time):
        '''
        takes an elevation array, a 'slope to horizon (radians)' array,
        and a solar altitude as inputs,
        and returns a (TILTED) array of visible points
        '''
        #elevG, hSlope_rad = self.slope2horz()
        #elevG, hSlope_rad = self.horizon_dispatch()
        solar_altitude = self.df['solar_altitude'].iloc[time]
        solar_altitude = np.deg2rad(90 - solar_altitude)
        shape = hSlope_rad.shape
        mask = np.zeros(shape)
        for k in range(0, shape[0]):
            for i in range(0, shape[0]):
                if hSlope_rad[i,k] > solar_altitude:
                    mask[i,k] = 1
                elif hSlope_rad[i,k] < solar_altitude:
                    mask[i,k] = 0
                else:
                    mask[i,k] = -1
                
        #tiltedElevG = elevG
        #tiltedMask = mask
        return mask
    
    @staticmethod
    def _bbox(array):
        '''

        '''
        rows = np.any(array, axis=1)
        cols = np.any(array, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]

        return rmin, rmax, cmin, cmax

    @staticmethod
    def _rerotate_mask(rot_grid, rot_mask, azimuth):   
        '''
        rotate mask back to original position, set non-1s to zeros
        '''
        
        #rotated_elevG, tiltedMask = self.invisiblePoints()
        #dimLength = self.resolution
        
        mask = ndimage.rotate(rot_mask, angle=azimuth, reshape=True, 
                                order=0, mode='constant', cval=np.nan)

        mask[np.isnan(mask)] = 0
        mask[mask == 0.5] = 0

        #create ref from the rotated elevation grid, set nans to zeros, extract extents from ref
        ref = ndimage.rotate(rot_grid, angle=azimuth, reshape=True, 
                                order=0, mode='constant', cval=np.nan)
        ref[np.isnan(ref)] = 0
        rmin, rmax, cmin, cmax = _bbox(array=ref)

        #clip extractMask using referenced extents, reset extractMask 0's to nan's
        mask = mask[rmin:rmax, rmin:cmax]
        mask[mask==0] = np.nan

        return mask
    
    @staticmethod
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
            col_stacker = np.zeros((mask[1],1))

            if mask.shape[0] == mask.shape[1]:
                for i in range(1,row_diff+1):
                    mask = np.append(mask, [row_stacker], axis=0)
                for i in range(1,col_diff+1):
                    mask = np.append(mask, col_stacker, axis=1)
            else:
                mask = np.zeros(target_shape)
            
        mask[mask==0] = np.nan

        return mask

    def 