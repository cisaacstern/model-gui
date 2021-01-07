import .pointdata as pointdata
import numpy as np
from scipy import interpolate, ndimage
import richdem as rd
from tempfile import TemporaryFile

class GridData(pointdata.PointData):
    
    def interpolate_grid(self):
        '''
        takes xyz pointcloud data, outputs nearest neighbor interpolation
        '''
        xyz = self.import_xyz()
        Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]

        xi = np.linspace(self.EAST_MIN, self.EAST_MAX, self.resolution)
        yi = np.linspace(self.NORTH_MIN, self.NORTH_MAX, self.resolution)

        return interpolate.griddata((Easting, Northing), Elevation, 
                                    (xi[None,:], yi[:,None]), method='nearest')
    
    def transform_grid(self):
        '''
        takes an interpolated grid, outputs gaussian, slope, & aspect arrays
        '''
        grid = self.interpolate_grid()
        gauss_grid = ndimage.gaussian_filter(grid, sigma=self.sigma)
        slope_grid, aspect_grid = self.calc_grid_attributes(grid=gauss_grid)
        return gauss_grid, slope_grid, aspect_grid
    
    def np2rdarray(self, in_array, no_data=-9999):
        out_array = rd.rdarray(in_array, no_data=no_data)
        out_array.projection = self.PROJECTION
        out_array.geotransform = self.geotransform
        return out_array
    
    def calc_grid_attributes(self, grid):
        '''
        given input grid, returns slope and aspect grids
        '''
        rda = self.np2rdarray(np.asarray(grid), -9999)

        slope_outfile = TemporaryFile()
        np.save(slope_outfile, rd.TerrainAttribute(rda, attrib='slope_radians'))
        _ = slope_outfile.seek(0)
        slope_grid = np.load(slope_outfile)
        slope_outfile.close()

        aspect_outfile = TemporaryFile()
        np.save(aspect_outfile, rd.TerrainAttribute(rda, attrib='aspect'))
        _ = aspect_outfile.seek(0)
        aspect_grid = np.load(aspect_outfile)
        aspect_grid[aspect_grid>180] = aspect_grid[aspect_grid>180]-360
        aspect_outfile.close()

        return slope_grid, aspect_grid