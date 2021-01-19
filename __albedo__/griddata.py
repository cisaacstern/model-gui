import albedo._albedo.pointdata as pointdata
#import _albedo.pointdata as pointdata
import numpy as np
from scipy import interpolate, ndimage
import richdem as rd
from tempfile import TemporaryFile

class GridData(pointdata.PointData):
    
    def elevation_grid(self):
        '''
        takes xyz pointcloud data, outputs nearestNeighbor interpolation
        '''
        xyz = self.datetime2xyz(choice='pointcloud')
        Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]

        xi = np.linspace(self.eastMin, self.eastMax, self.resolution)
        yi = np.linspace(self.northMin, self.northMax, self.resolution)

        return interpolate.griddata((Easting, Northing), Elevation, 
                                    (xi[None,:], yi[:,None]), method='nearest')
    
    def griddata_transforms(self):
        '''
        takes a nearestNeighbor grid, outputs gaussian, slope, & aspect arrays
        '''
        inputGrid = self.elevation_grid()
        blurredArray = ndimage.gaussian_filter(inputGrid, sigma=self.sigma)
        slopeArray, aspectArray = self.raster_slope_aspect(blurredArray)
        return blurredArray, slopeArray, aspectArray
    
    def np2rdarray(self, in_array, no_data=-9999):
        out_array = rd.rdarray(in_array, no_data=no_data)
        out_array.projection = self.projection
        out_array.geotransform = self.geotransform
        return out_array
    
    def raster_slope_aspect(self, gaussianArray):
        '''
        given a gaussian array, returns slope and aspect arrays
        '''
        rda = self.np2rdarray(np.asarray(gaussianArray), -9999)

        slopeOutfile = TemporaryFile()
        np.save(slopeOutfile, rd.TerrainAttribute(rda, attrib='slope_radians', 
                                                  zscale=self.vertEx))
        _ = slopeOutfile.seek(0)
        slopeArray = np.load(slopeOutfile)
        slopeOutfile.close()

        aspectOutfile = TemporaryFile()
        np.save(aspectOutfile, rd.TerrainAttribute(rda, attrib='aspect'))
        _ = aspectOutfile.seek(0)
        aspectArray = np.load(aspectOutfile)
        aspectArray[aspectArray>180] = aspectArray[aspectArray>180]-360
        aspectOutfile.close()

        return slopeArray, aspectArray