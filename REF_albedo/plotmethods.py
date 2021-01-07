import albedo._albedo.setaxes as setaxes
#import _albedo.setaxes as setaxes
import param
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import numpy as np
from datetime import datetime, timedelta

import pandas as pd

class PlotMethods(setaxes.SetAxes):
    
    @param.depends('run_state', 'date', 'elev', 'choose3d')
    def axes3d(self, figsize=(6,6), topMargin=1.2, bottomMargin=0):
        if self.run_state == True:
            pass
        else:
            plt.close()
            fig = plt.figure(figsize=figsize)
            ax = fig.add_subplot(111, projection='3d')

            if self.choose3d:
                if 'Raw Lidar' in self.choose3d:
                    xyz = self.datetime2xyz(choice='raw')
                    Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]
                    ax.scatter(Easting, Northing, Elevation,
                               cmap='viridis', c=Elevation)
                
                if 'Pointcloud' in self.choose3d:
                    xyz = self.datetime2xyz(choice='pointcloud')
                    Easting, Northing, Elevation = xyz[:,0], xyz[:,1], xyz[:,2]
                    ax.scatter(Easting, Northing, Elevation,
                               cmap='viridis', c=Elevation)

                if 'Planar Fit' in self.choose3d:
                    XYZ = self.pFit()
                    X, Y, Z = XYZ[:,:,0], XYZ[:,:,1], XYZ[:,:,2]
                    ax.plot_surface(X, Y, Z, color='r', 
                                    rstride=1, cstride=1, alpha=0.4)

            ax.view_init(elev=self.elev, azim=self.azim)
            ax.set_xlim(320977, 320980)
            ax.set_xlabel('Easting')
            ax.set_ylim(4168144, 4168147)
            ax.set_ylabel('Northing')
            ax.set_zlim(2941.977, 2948.356)
            ax.set_zlabel('Elevation')
            plt.subplots_adjust(top=topMargin, bottom=bottomMargin) 
            plt.close()
            return fig
    
    @param.depends('date', 'resolution', 'sigma', 'time', 'activateMask')
    def triptych(self, figsize=(12,5), wspace=0.05, hspace=0, leftMargin=0.05, 
                 rightMargin=0.97, topMargin=0.79, bottomMargin=0.1):
        plt.close()
        fig, ax = plt.subplots(1,3, figsize=figsize, dpi=self.dpi)
        canvas = FigureCanvasAgg(fig)

        ds = self.date_string
        line2 = f'\nR, S ={(self.resolution,self.sigma)}'

        titles = [f'{ds}: Elevation'+line2, f'{ds}: Slope'+line2,
                  f'{ds}: Aspect (South=0, East +)'+line2]

        if self.activateMask == 'Overlay':
            imgs = [self.masked_elev, self.masked_slope, self.masked_aspect]
        elif self.activateMask == 'Remove':
            imgs = [self.elevRast, self.slopeRast, self.aspectRast]

        cmaps = ['viridis', 'YlOrBr', 'hsv']
        cmapRanges = [(np.min(self.elevRast), np.max(self.elevRast)),
                      (np.min(self.slopeRast), np.max(self.slopeRast)),
                      (-180, 180)]

        ticks = np.linspace(0, self.resolution-1, 4)
        xlabels = [str(self.eastMin)[-2:], str(self.eastMin+1)[-2:],
                   str(self.eastMin+2)[-2:], str(self.eastMax)[-2:]]
        ylabels = [str(self.northMin)[-2:], str(self.northMin+1)[-2:],
                   str(self.northMin+2)[-2:], str(self.northMax)[-2:]]

        ims = []
        for i in range(3):
            img, cmap = imgs[i], cmaps[i]
            im = ax[i].imshow(img, origin='lower', cmap=cmap,
                              vmin=cmapRanges[i][0], vmax=cmapRanges[i][1])
            ims.append(im)
            ax[i].set_xticks(ticks=ticks)
            ax[i].set_xticklabels(labels=xlabels)
            ax[i].set_yticks(ticks=ticks)
            if i == 0:
                ax[i].set_yticklabels(labels=ylabels)
                ax[i].set_ylabel(f'Northing (+{str(self.northMin)[:-2]}e2)')
            else:
                ax[i].set_yticklabels(labels=[])
            if i == 1:
                ax[i].set_xlabel(f'Easting (+{str(self.eastMin)[:-2]}e2)')
            ax[i].set_aspect("equal")

        plt.subplots_adjust(left=leftMargin, right=rightMargin,
                            top=topMargin, bottom=bottomMargin,
                            wspace=wspace, hspace=hspace)

        for i in range(3):
            p = ax[i].get_position().get_points().flatten()
            ax_cbar = fig.add_axes([p[0], 0.85, p[2]-p[0], 0.05])
            ax_cbar.set_title(titles[i], loc='left')
            cb = plt.colorbar(ims[i], cax=ax_cbar, orientation='horizontal')
            if i == 2:
                cbar_ticks = [-180, -135, -90, -45, 0, 45, 90, 135, 180]
                cb.set_ticks(cbar_ticks)

        if self.run_state == True:
            canvas.draw() # Retrieve a view on the renderer buffer
            buf = canvas.buffer_rgba()
            X = np.asarray(buf) # convert to a NumPy array
            plt.close()
            return X
        else:
            plt.close()
            return fig
    
    @param.depends('date', 'time', 'bins')
    def polarAxes(self, figsize=(3.5,5), topMargin=1, bottomMargin=0,
                  leftMargin=0.1, rightMargin=0.92):
        
        df = self.dataframe

        plt.close()
        fig = plt.figure(figsize=figsize, dpi=self.dpi)
        canvas = FigureCanvasAgg(fig)
        
        ax = fig.add_subplot(111, projection='polar')
        ax.set_theta_zero_location('N')
        ax.set_xticks(([np.deg2rad(0), np.deg2rad(45), np.deg2rad(90),
                        np.deg2rad(135), np.deg2rad(180), np.deg2rad(225),
                        np.deg2rad(270), np.deg2rad(315)]))
        xlbls = np.array(['N','45','E','135','S','225','W','315'])
        ax.set_xticklabels(xlbls, rotation="vertical", size=12)
        ax.tick_params(axis='x', pad = 0.5)
        ax.set_theta_direction(-1)
        ax.set_rmin(0)
        ax.set_rmax(90)
        ax.set_rlabel_position(90)
        
        if self.bins != 'Max':
            col = df['bin_assignment']
            xs  = [np.deg2rad(self.angle_dict[entry]) for entry in col]
            x   = np.deg2rad(self.angle_dict[col.iloc[self.time]])
        else:
            col = df['solarAzimuth']
            xs  = np.deg2rad(col)
            x   = np.deg2rad(col.iloc[self.time])

        ys = df['solarAltitude']
        y  = df['solarAltitude'].iloc[self.time]

        ax.scatter(xs,ys, s=10, c='orange',alpha=0.5)
        ax.scatter(x, y, s=500, c='gold',alpha=1)
        
        self.dt_str = df['MeasDateTime'].iloc[self.time]
        line1=f'{self.dt_str} Sun Position'
        line2=f'Azi, SZA={np.around((np.rad2deg(x),y),1)}, Bins={self.bins}'

        plt.subplots_adjust(top=topMargin, bottom=bottomMargin,
                            left=leftMargin, right=rightMargin)

        p = ax.get_position().get_points().flatten()
        ax_cbar = fig.add_axes([p[0]+0.085, 0.85, p[2]-p[0], 0.05])
        ax_cbar.set_title(line1+'\n'+line2, loc='left')
        ax_cbar.axis('off')

        if self.run_state == True:
            canvas.draw() # Retrieve a view on the renderer buffer
            buf = canvas.buffer_rgba()
            X = np.asarray(buf) # convert to a NumPy array
            plt.close()
            return X
        else:
            plt.close()
            return fig
        
    @param.depends('date', 'resolution', 'sigma', 'time', 'activateMask')
    def diptych(self, figsize=(8.25,5), topMargin=0.85, bottomMargin=0.05,
                leftMargin=0.095, rightMargin=0.95, wspace=0.1, hspace=0):
        '''
        generates and plots a 'magma' themed M raster and 
        the direct rad shade mask for the given date & time
        '''
        plt.close()
        fig, ax = plt.subplots(1,2, figsize=figsize, dpi=self.dpi)
        
        canvas = FigureCanvasAgg(fig)

        line2 = f'\nR, S, B={(self.resolution,self.sigma,self.bins)}'
        title1 = f'{self.dt_str}: Terrain Correction'+line2
        title2 = f'{self.dt_str}: Current Visibility'+line2
        titles = [title1, title2]

        if self.activateMask == 'Overlay':
            imgs = [self.masked_m, self.mask]
        elif self.activateMask == 'Remove':
            imgs = [self.m, self.mask]

        cmaps = ['magma', 'binary']
        cmapRanges = [(0,2), (0, 1)]

        ticks = np.linspace(0, self.resolution-1, 4)
        xlabels = [str(self.eastMin)[-2:], str(self.eastMin+1)[-2:],
                   str(self.eastMin+2)[-2:], str(self.eastMax)[-2:]]
        ylabels = [str(self.northMin)[-2:], str(self.northMin+1)[-2:],
                   str(self.northMin+2)[-2:], str(self.northMax)[-2:]]

        ims = []
        for i in range(2):
            img, cmap = imgs[i], cmaps[i]
            im = ax[i].imshow(img, origin='lower', cmap=cmap,
                              vmin=cmapRanges[i][0], vmax=cmapRanges[i][1])
            ims.append(im)
            ax[i].set_xticks(ticks=ticks)
            ax[i].set_xticklabels(labels=xlabels)
            ax[i].set_yticks(ticks=ticks)
            if i == 0:
                ax[i].set_yticklabels(labels=ylabels)
                ax[i].set_ylabel(f'Northing (+{str(self.northMin)[:-2]}e2)')
            else:
                ax[i].set_yticklabels(labels=[])
            if i == 0:
                ax[i].set_xlabel(f'Easting (+{str(self.eastMin)[:-2]}e2)')
            ax[i].set_aspect("equal")

        plt.subplots_adjust(left=leftMargin, right=rightMargin,
                                top=topMargin, bottom=bottomMargin,
                                wspace=wspace, hspace=hspace)

        for i in range(2):
            p = ax[i].get_position().get_points().flatten()
            ax_cbar = fig.add_axes([p[0], 0.85, p[2]-p[0], 0.05])
            ax_cbar.set_title(titles[i], loc='left')
            cb = plt.colorbar(ims[i], cax=ax_cbar, orientation='horizontal')
            if i == 1:
                cb.set_ticks([0, 1])
                cb.set_ticklabels("Visible", "Shaded")
        
        if self.run_state == True:
            canvas.draw() # Retrieve a view on the renderer buffer
            buf = canvas.buffer_rgba()
            X = np.asarray(buf) # convert to a NumPy array
            plt.close()
            return X
        else:
            plt.close()
            return fig
        
    def timeSeries_Plot(self, df, mx):
        '''
        plots a time series, given set of times and a tuple of y's.
        '''
        plt.close()
        #figure and three axes
        fig, ax_rad = self.fig, self.ax
        
        canvas = FigureCanvasAgg(fig)
        
        ax_m, ax_alpha, ax_viz = self.par1, self.par2, self.par3

        #setting up the plot title
        t_dict = self.param.time.names
        sunrise_sunset = f'({list(t_dict)[0]}-{list(t_dict)[-1]})'
        line1 = f'{self.date_string} {sunrise_sunset};'
        line2 = f' R, S, B={[self.resolution,self.sigma,self.bins]}'
        title = line1+line2
        ax_rad.set_title(title, loc='left', fontsize=12)

        #x-axis vals (in UTC) & labels (in PT)
        times = df['UTC_datetime'] - timedelta(hours=self.UTC_offset)
        time_labels = [t.strftime("%H:%M") for t in times]
        time_labels[0] = ''
        ax_rad.set_xticks(times[::4])
        ax_rad.set_xticklabels(time_labels[::4])

        #assigning curve values
        cols = df.columns
        vals = [
            tuple(df[next(col for col in cols if col.startswith('downward looking'))]),
            tuple(df[next(col for col in cols if col.startswith('upward looking diffuse'))]),
            tuple(df[next(col for col in cols if col.startswith('upward looking solar'))] 
                  - df[next(col for col in cols if col.startswith('upward looking diffuse'))]),
            tuple(df['M_planar']),
            tuple(df['Albedo_planar']),
            tuple(df['raster_meanM']),
            tuple(df['raster_meanALPHA']),
            tuple(df['maskedmeanM']),
            tuple(df['maskedAlbedo']),
            tuple(df['viz_percent'])
        ]
        #variable assignment
        (globalup, diffusedwn, directdwn, M_planar, Albedo_planar, 
         raster_meanM, raster_meanALPHA, maskedmeanM, maskedAlbedo, 
         viz_percent) = vals    

        #measurements
        m = {
            'Global Up': [globalup, 'orange'],
            'Direct Dwn': [directdwn, 'salmon'],
            'Diffuse Dwn': [diffusedwn, 'peachpuff']
        }

        #products
        p = {'M':[M_planar,'solid'],     'Alpha':[Albedo_planar,'solid'],    'IDR':['planarIDR','green']}
        r = {'M':[raster_meanM,'dashed'],'Alpha':[raster_meanALPHA,'dashed'],'IDR':["rIDR_data",'dgreen']}
        h = {'M':[maskedmeanM,'dotted'],'Alpha':[maskedAlbedo,'dotted'],   'IDR':["hIDR_data",'ddgreen']}
        v = {'v':[viz_percent, 'k']}

        #unification
        plot = {
            **{m[pick][0]:[m[pick][1],'raw'] 
               for pick in self.set_measurements},
            **{p[pick][0]:[p[pick][1], pick] 
               for pick in self.set_planar_curves},
            **{r[pick][0]:[r[pick][1], pick] 
               for pick in self.set_raster_curves},
            **{h[pick][0]:[h[pick][1], pick] 
               for pick in self.set_horizon_curves},
            **{v['v'][0]:[v['v'][1], 'viz']}
        } 

        #plot
        for data, metadata in zip(plot.keys(), plot.values()):
            ax_rad.plot(times, np.zeros((len(times))), alpha=0) #time4host
            if metadata[1] in ('raw', 'IDR'):
                ax_rad.plot(times[:mx], data[:mx], c=metadata[0])
            elif metadata[1] == 'M':
                ax_m.plot(times[:mx], data[:mx], ls=metadata[0], c='mediumorchid')
            elif metadata[1] == 'Alpha':
                ax_alpha.plot(times[:mx], data[:mx], ls=metadata[0], c='darkturquoise')
            elif metadata[1] == 'viz':
                if self.set_visibile_curve:
                    ax_viz.plot(times[:mx], data[:mx], c=metadata[0], alpha=0.5)
            else:
                raise KeyError('Plot data|metadata error.')

        if self.run_state == True:
            canvas.draw() # Retrieve a view on the renderer buffer
            buf = canvas.buffer_rgba()
            X = np.asarray(buf) # convert to a NumPy array
            plt.close()
            return X
        else:
            plt.close()
            return fig
        