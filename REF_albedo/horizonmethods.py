import albedo._albedo.setframe as setframe
#import _albedo.setframe as setframe
from scipy import ndimage
import numpy as np

class HorizonMethods(setframe.SetFrame):
    
    def rotate2azimuth(self):
        '''
        rotates an elevation raster so that North is re-referenced to be
        facing the solar azimuth.
        '''
        df = self.dataframe
        if self.bins != 'Max':
            col = df['bin_assignment']
            azimuth = self.angle_dict[col.iloc[self.time]]
        else:
            col = df['solarAzimuth']
            azimuth = col.iloc[self.time]
            
        return ndimage.rotate(self.elevRast, angle=(-azimuth), reshape=True, 
                              order=0, mode='constant', cval=np.nan)
    
    def fwdHorz2D(self):
        '''
        elevG is the blurred *AND ROTATED* elevation grid. horzPt[] is an empty
        *2D array* to be filled with the horzPts for each cell in THE ROTATED elevation grid
        the horzPt for a given elevG[i, k] is expressed as an index value of elevG[]
        '''
        def SLOPE2D(gzi, ii, jj, kk):
            '''
            gzi[] is the elevation grid, ii and jj are row indicies, kk is the column index
            '''
            if gzi[jj, kk] >= gzi[ii, kk]:
                return (gzi[jj, kk] - gzi[ii, kk])/(jj-ii)
            else:
                return 0
        #beginning of the outer function    
        elevG = self.rotate2azimuth()
        horzPt = np.zeros(elevG.shape, dtype=int)
        #nHorz is an integer value equal to the height of the array elevG[]
        nHorz = horzPt.shape[0]
        for k in range(0, nHorz - 1):
            horzPt[nHorz - 1, k] = nHorz - 1 #the first entry is its own horizon
            for i in range(nHorz - 2, -1, -1): #loop from next-to-end backward to beginning
                j = i + 1
                HorzJ = horzPt[j, k]
                slopeItoJ = SLOPE2D(elevG,i,j,k)
                slopeItoHorzJ = SLOPE2D(elevG,i,HorzJ,k)
                while slopeItoJ < slopeItoHorzJ:
                    j = HorzJ
                    HorzJ = horzPt[j, k]
                    slopeItoJ = SLOPE2D(elevG,i,j,k)
                    slopeItoHorzJ = SLOPE2D(elevG,i,HorzJ,k)
                if slopeItoJ>slopeItoHorzJ:
                    horzPt[i, k] = j
                elif slopeItoJ == 0:
                    horzPt[i, k] = i
                else:
                    horzPt[i, k] = HorzJ
        return elevG, horzPt
    
    def slope2horz(self):
        '''
        takes a rotated elevation grid and a corresponding horzPt array,
        from self.fwdHorz2D, and calculates the slope from each point on
        the elevation grid to its horizon point in the horzPt array.
        returns the elevation grid and a 'slope to horizon (radians)' array
        '''
        elevGrid, horzPt_array = self.fwdHorz2D()

        shape = elevGrid.shape
        hSlope_rad = np.zeros(shape)
        for k in range(0, shape[0]):
            for i in range(0, shape[0]):
                hSlope_rad[i,k] = np.arctan2(elevGrid[horzPt_array[i,k], k] - elevGrid[i,k], 
                                             ((0.01*horzPt_array[i,k]) - (0.01*i)))
        return elevGrid, hSlope_rad
        
    #Second set of functions---ALTITUDE DEPENDANT---begins here
    def horizon_dispatch(self):
        if self.bins != 'Max':
            if self.run_state==True:
                col = self.dataframe['bin_assignment']                    
                current_bin = col.iloc[self.time]
                trigger_update = (True
                                  if current_bin != col.iloc[self.time-1]
                                  else False)
                if trigger_update:
                    self.horizon_package = self.slope2horz()
                    return self.horizon_package
                else:
                    return self.horizon_package
            else:
                return self.slope2horz()
        else:
            return self.slope2horz()
    
    def invisiblePoints(self):
        '''
        takes an elevation array, a 'slope to horizon (radians)' array,
        and a solar altitude as inputs,
        and returns a (TILTED) array of visible points
        '''
        #elevG, hSlope_rad = self.slope2horz()
        elevG, hSlope_rad = self.horizon_dispatch()
        solar_altitude = self.dataframe['solarAltitude'].iloc[self.time]
        solar_altitude = np.deg2rad(90 - solar_altitude)
        shape = hSlope_rad.shape
        shadeMask = np.zeros(shape)
        for k in range(0, shape[0]):
            for i in range(0, shape[0]):
                if hSlope_rad[i,k] > solar_altitude:
                    shadeMask[i,k] = 1
                elif hSlope_rad[i,k] < solar_altitude:
                    shadeMask[i,k] = 0
                else:
                    shadeMask[i,k] = -1
                
        tiltedElevG = elevG
        tiltedMask = shadeMask
        return tiltedElevG, tiltedMask

    #---RE-ROTATION---
    def rerotM_2(self):   
        '''
        
        '''
        def bbox2(img):
            rows = np.any(img, axis=1)
            cols = np.any(img, axis=0)
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]

            return rmin, rmax, cmin, cmax
        #rotate mask back to original position, set non-1s to zeros
        
        rotated_elevG, tiltedMask = self.invisiblePoints()
        dimLength = self.resolution
        
        df = self.dataframe
        if self.bins != 'Max':
            col = df['bin_assignment']
            azimuth = self.angle_dict[col.iloc[self.time]]
        else:
            col = df['solarAzimuth']
            azimuth = col.iloc[self.time]
        
        rerotatedMask = ndimage.rotate(tiltedMask, angle=azimuth, reshape=True,
                                       order=0, mode='constant', cval=np.nan)
        
        rerotatedMask[np.isnan(rerotatedMask)] = 0
        rerotatedMask[rerotatedMask == 0.5] = 0

        #create a reference from the rotated elevation grid, and set nans to zeros
        refExtents = ndimage.rotate(rotated_elevG, angle=azimuth, 
                                    reshape=True, order=0, mode='constant', cval=np.nan)
        refExtents[np.isnan(refExtents)] = 0

        #extract extents from refExtents
        rmin, rmax, cmin, cmax = bbox2(refExtents)

        #clip extractMask using referenced extents, reset extractMask 0's to nan's
        rerotatedMask = rerotatedMask[rmin:rmax, rmin:cmax]
        rerotatedMask[rerotatedMask==0] = np.nan

        targetShape = (dimLength, dimLength)
        #tack on some extra rows, if needed
        if rerotatedMask.shape == targetShape:
            rerotatedMask = rerotatedMask
        elif rerotatedMask.shape != targetShape:
            rowDiff = targetShape[0] - rerotatedMask.shape[0]
            colDiff = targetShape[1] - rerotatedMask.shape[1]
            rowStacker = np.zeros((rerotatedMask.shape[0]))
            colStacker = np.zeros((targetShape[1],1))
            #assert (rerotatedMask.shape[0] == rerotatedMask.shape[1]), "This puppy aint square!"
            if rerotatedMask.shape[0] == rerotatedMask.shape[1]:
                for q in range(1,rowDiff+1):
                    rerotatedMask = np.append(rerotatedMask, [rowStacker], axis=0)
                for q in range(1,colDiff+1):
                    rerotatedMask = np.append(rerotatedMask, colStacker, axis=1)
            else:
                rerotatedMask = np.zeros(targetShape)
        else:
            print('mask shape mismatch error')
            
            
        rerotatedMask[rerotatedMask==0] = np.nan


        return rerotatedMask