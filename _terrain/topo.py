import os
import numpy as np
from scipy import linalg, interpolate, ndimage
from tempfile import TemporaryFile
import richdem as rd
import _terrain.config as c

class Topography():
    '''
    I try to avoid unnecesary complexity.
    But these functions all reuse the same xyz columnar data.
    So I decided to define them all in one class and initialize xyz as an shared attribute.
    '''

    def __init__(self, topo_fname):
         
        def import_xyz(topo_path, topo_fname, bounds):
            '''
            takes a path and filename, finds and imports corresponding topography data
            bounds is a 6-member array of floats, as follows:
                [east_min, east_max, north_min, north_max, elev_max, elev_min]
            '''
            xyz = np.genfromtxt(fname=os.path.join(topo_path, topo_fname), delimiter=',', skip_header=1)
            
            Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]
            assert(not(np.any((Easting < bounds[0])|(Easting > bounds[1])))), 'Easting out of range.'
            assert(not(np.any((Northing < bounds[2])|(Northing > bounds[3])))), 'Northing out of range.'
            assert(not(np.any((Elevation < bounds[4])|(Elevation > bounds[5])))), 'Elevation out of range.'

            return xyz

        self.xyz = import_xyz(topo_path=c.TOPO_PATH, topo_fname=topo_fname, bounds=c.BOUNDS)

    #---Planar methods

    def planar_attrib(self):
        '''
        finds the slope and aspect for the planar fit returned by inner function fit_plane()
        the equations used herein are my rewrites of methods described at the following two links:
            https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/how-slope-works.htm
            https://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/how-aspect-works.htm
        '''
        def fit_plane(xyz):
            '''
            returns a least squares plane for input set of xyz columnar topographic data
            '''
            x, y, z = xyz[:,0], xyz[:,1], xyz[:,2]
            
            data = np.c_[x,y,z]

            # regular grid covering the domain of the data
            mn = np.min(data, axis=0)
            mx = np.max(data, axis=0)
            X,Y = np.meshgrid(np.linspace(mn[0], mx[0], 20), np.linspace(mn[1], mx[1], 20))

            # best-fit linear plane
            A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
            C,_,_,_ = linalg.lstsq(A, data[:,2])

            # evaluate it on grid
            Z = C[0]*X + C[1]*Y + C[2]

            return np.dstack((X,Y,Z))

        XYZ = fit_plane(xyz=self.xyz)
        
        X, Y, Z = XYZ[:,:,0], XYZ[:,:,1], XYZ[:,:,2] 
        J, K, L = X[0,0], Y[0,0], Z[0,0]
        Q, R, S = X[19,0], Y[19,0], Z[19,0]

        opposite = np.abs(L-S)
        adjacent = np.abs(R-K)
        dzdy = opposite/adjacent

        J, K, L = X[19,0], Y[19,0], Z[19,0]
        Q, R, S = X[19,19], Y[19,19], Z[19,19]

        opposite = np.abs(L-S)
        adjacent = np.abs(Q-J)
        dzdx = opposite/adjacent
        
        slope = np.rad2deg(np.arctan(np.sqrt((dzdx**2) + (dzdy**2))))
        aspect = np.rad2deg(np.arctan2(dzdx, -dzdy))

        return slope, aspect

    #---Grid Methods

    def return_grids(self, resolution, sigma):
        '''
        interpolates a grid from xyz columnar topographic data,
        then outputs gaussian, slope, & aspect arrays
        '''
        def interpolate_grid(xyz):
            '''
            takes xyz pointcloud data, outputs nearest neighbor interpolation
            EAST and NORTH bounds are defined in _terrain/_settings/config.toml,
            and initalized in _terrain/__init__.py
            '''
            Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]

            xi = np.linspace(c.EAST_MIN, c.EAST_MAX, resolution)
            yi = np.linspace(c.NORTH_MIN, c.NORTH_MAX, resolution)

            return interpolate.griddata((Easting, Northing), Elevation, 
                                        (xi[None,:], yi[:,None]), method='nearest')

        def np2rdarray(in_array, geotransform, no_data=-9999):
            '''
            slope and aspect calculations are performed by richdem, which
            requires data in rdarray format. this function converts numpy
            arrays into rdarrays.
            '''
            out_array = rd.rdarray(in_array, no_data=no_data)
            out_array.projection = c.PROJECTION
            cell_scale = np.around(a=c.SIDE_LEN/resolution, decimals=5)
            out_array.geotransform = [0, cell_scale, 0, 0, 0, cell_scale]
            return out_array
        
        def calc_grid_attributes(grid):
            '''
            given input grid, returns slope and aspect grids
            '''
            rda = np2rdarray(np.asarray(grid), -9999)

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

        grid = interpolate_grid(xyz=self.xyz)
        gauss_grid = ndimage.gaussian_filter(grid, sigma=sigma)
        slope_grid, aspect_grid = calc_grid_attributes(grid=gauss_grid)

        return gauss_grid, slope_grid, aspect_grid


#TEST SECTION
'''
print(c.TOPO_LIST[0])
test = Topography(c.TOPO_LIST[0])
print(test.xyz)
print(test.planar_attrib())
print(test.return_grids(30, 2.0))
'''
