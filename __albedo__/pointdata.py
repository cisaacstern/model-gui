import albedo._albedo.parameters as parameters
#import _albedo.parameters as parameters
import param
import numpy as np
from scipy import linalg

class PointData(parameters.Parameters):
    
    @param.depends('date')
    def set_filename(self):
        self.filename = self.pointclouds[self.date]
    
    def datetime2xyz(self, choice):
        '''
        takes a filename, finds and imports corresponding pointcloud data
        '''
        if choice=='raw':
            fn = self.filename[:-8]+'PC.csv'
            xyz = np.genfromtxt(fname=self.raw_directory+'/'+fn, 
                                delimiter=',', skip_header=1)
        else:
            xyz = np.genfromtxt(fname=self.pointcloud_directory+'/'
                                +self.filename, delimiter=',', skip_header=1)
        
        Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]
        assert(not(np.any((Easting < self.eastMin)|(Easting > self.eastMax)))), 'Easting out of range.'
        assert(not(np.any((Northing < self.northMin)|(Northing > self.northMax)))), 'Northing out of range.'
        #assert(not(np.any((Elevation < 2941.977)|(Elevation > 2948.356)))), 'Elevation out of range.'
        
        return xyz
    
    def pFit(self):
        xyz = self.datetime2xyz(choice='pointcloud')
        x, y, z = xyz[:,0], xyz[:,1], xyz[:,2]
        
        data = np.c_[x,y,z]

        # regular grid covering the domain of the data
        mn = np.min(data, axis=0)
        mx = np.max(data, axis=0)
        X,Y = np.meshgrid(np.linspace(mn[0], mx[0], 20), np.linspace(mn[1], mx[1], 20))

        # best-fit linear plane
        A = np.c_[data[:,0], data[:,1], np.ones(data.shape[0])]
        C,_,_,_ = linalg.lstsq(A, data[:,2])    # coefficients

        # evaluate it on grid
        Z = C[0]*X + C[1]*Y + C[2]

        return np.dstack((X,Y,Z))
    
    def planar_slope_aspect(self):
        
        XYZ = self.pFit()
        
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