import albedo._albedo.plotmethods as plotmethods
#import _albedo.plotmethods as plotmethods
import param
import time
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import subprocess
import json

class RunModel(plotmethods.PlotMethods):
      
    def albedo(self, df, row, choice):
            '''
            
            '''
            for col in df.columns:
                if col.startswith('downward looking'):
                    D_up = df[col].iloc[row]
                if col.startswith('upward looking diffuse'):
                    D_down = df[col].iloc[row]
                if col.startswith('upward looking solar'):
                    B_down = df[col].iloc[row]
            B_down = B_down - D_down

            if choice == 'planar':
                c = df['M_planar'].iloc[row]
            elif choice == 'raster':
                c = df['raster_meanM'].iloc[row]
            elif choice == 'masked':
                c = df['maskedmeanM'].iloc[row]

            return D_up/((c*B_down)+D_down)
    
    def update_run_log(self, local_t):
        '''
        
        '''
        k, v = list(self.dictionary.keys()), list(self.dictionary.values())
        const_key, const_values = k[0], v[0]
        config_key, config_values_dict = k[1], v[1]
        config_value_keys = list(config_values_dict.keys())
        config_value_vals = list(config_values_dict.values())

        date_key, date_val = config_value_keys[0], config_value_vals[0]
        raster_key, raster_vals = config_value_keys[1], config_value_vals[1]
        xgeo_key, xgeo_val = config_value_keys[2], config_value_vals[2]
        azi_key, azi_vals = config_value_keys[3], config_value_vals[3]
        self.log += f"""\n{local_t}, model queued with config:
        {date_key}: {date_val}
        {raster_key}: {raster_vals}
        {xgeo_key}: {xgeo_val}
        {azi_key}: {list(azi_vals.keys())[0]}: {list(azi_vals.values())[0][0]}\n"""

        if self.bins != 'Max':
            bins = list(azi_vals.values())[0][1]
            vals = [str(np.around(val,1)) for val in bins]
            vals = [' '+val if len(val)==4 else val for val in vals]
            vals = ['  '+val if len(val)==3 else val for val in vals]
            newline = "\n"
            cycles = int((len(bins))/8)*8
            lines = ["            "+', '.join(vals[:8]) if c==0
                     else ', '.join(vals[c:c+8]) for c in range(0, cycles, 8)]
            tabbed_newline = newline+"            "
            self.log += f"""{tabbed_newline.join(lines)}"""
        else:
            pass
        
        return
    
    def subprocess_calls(self):
        '''
        
        '''
        s = self.session
        ID = self.ID
        
        raw_fn = self.filename[:-8]+'PC.csv'
        rad_fn = self.filename[:-8]+'radiometers.csv'
        raw_out = 'raw.csv'
        rad_out = 'radiometers.csv'
        nbpc_out= 'snowsurface.csv'
        
        subprocess.run(['mkdir', f'exports/{s}/{ID}'])
        subprocess.run(['mkdir', f'exports/{s}/{ID}/inputs'])
        subprocess.run(['mkdir', f'exports/{s}/{ID}/outputs'])
        subprocess.run(['mkdir', f'exports/{s}/{ID}/outputs/arrays'])
                
        subprocess.run(['cp', f'data/pointclouds/{self.filename}', f'exports/{s}/{ID}/inputs/{nbpc_out}'])
        subprocess.run(['cp', f'data/radiometers/{rad_fn}', f'exports/{s}/{ID}/inputs/{rad_out}'])
        subprocess.run(['cp', f'data/raw/{raw_fn}',  f'exports/{s}/{ID}/inputs/{raw_out}'])
        return
    
    def export_arrays(self, m_arr, mask_arr):
        '''
        
        '''
        s = self.session
        ID = self.ID
        #save arrays
        arrs = [self.pFit(), self.elevRast, self.slopeRast, self.aspectRast,
               m_arr, mask_arr]
        names = ['planar_fit.npy', 'elevation.npy', 'slope.npy', 'aspect.npy',
                 'M.npy', 'masks.npy']
        for a, n in zip(arrs, names):
            np.save(f'exports/{s}/{ID}/outputs/arrays/{n}', a)
        return
            
    def write_mp4(self, img_arrays):
        '''
        
        '''
        s = self.session
        ID = self.ID
        # Set up formatting for the movie files
        fig = plt.figure(tight_layout=True, dpi=300)
        plt.axis('off')
        ims = [(plt.imshow(img),) for img in img_arrays]
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=5, metadata=dict(artist='Me'), bitrate=1800)
        im_ani = animation.ArtistAnimation(fig, ims, interval=200, repeat_delay=3000, blit=False)
        im_ani.save(f'exports/{s}/{ID}/outputs/{self.ID}.mp4', writer=writer)
        return
    
    def dump_json(self):
        '''
        
        '''
        s = self.session
        ID = self.ID
        with open(f'exports/{s}/{ID}/outputs/config.json', 'w') as outfile:
            json.dump(self.dictionary, outfile, indent=4)
        return
    
    def save_log(self):
        '''
        
        '''
        s = self.session
        ID = self.ID
        with open(f'exports/{s}/{ID}/outputs/build_log.txt', 'w') as outfile:
            log = self.log.replace('<pre style="color:lime">', '')
            log = log.replace('</pre>', '')
            outfile.write(log)
        return
    
    def export_df(self, df):
        '''
        
        '''
        s = self.session
        ID = self.ID
        #export dataframe
        df.to_csv(f'exports/{s}/{ID}/outputs/dataframe.csv')
        return
    
    def zip_archive(self):
        '''
        
        '''
        s = self.session
        ID = self.ID
        subprocess.run(['zip', '-r', f'{ID}.zip', f'{ID}'], cwd=f'exports/{s}')
        return
    
    @param.depends('run')
    def run_model(self): 
        '''
        
        '''
        if self.run == False:
            pass
        elif self.run == True:
            self.run_state = True
            start_t = time.time()
            local_t = time.ctime(start_t)
            self.update_run_log(local_t)
            
            #runnnn!
            plt.close('all') 
            
            self.subprocess_calls()
            self.log += '\nCreated model directory on disk.'
            
            df = self.dataframe.copy(deep=True)
            ncols = self.dataframe.shape[0]
            self.progress.max = (ncols-1)+10
            self.log += '\nCreated model dataframe'
            
            self.log += '\nAdding planar & raster albedo to dataframe...'
            #PLANAR M + ALBEDO
            self.p_slope, self.p_aspect = self.planar_slope_aspect()
            Mp_list = [self.M_calculation(df, row, choice='planar') 
                       for row in range(ncols)]
            df.insert(8, 'M_planar', Mp_list)
            Ap_list = [self.albedo(df, row, choice='planar')
                       for row in range(ncols)]
            df.insert(9, 'Albedo_planar', Ap_list)
            #RASTER meanM and RASTER_mean_ALPHA
            meanM_list = [
                np.mean(self.M_calculation(df=df, row=row, choice='raster')) 
                for row in range(ncols)]
            df.insert(10, 'raster_meanM', meanM_list)
            meanAlpha_list = [self.albedo(df, row, choice = 'raster') 
                              for row in range(ncols)]
            df.insert(11, 'raster_meanALPHA', meanAlpha_list)
            self.log += 'Complete'
            
            self.log += '\nRunning horizon model...'     
            maskedmeanM_list, viz_percent_list, img_arrays = [], [], []   
            for index in range(ncols):
                plt.close('all')
                #trigger new raster set
                self.time = index
                #calculate viz %
                unique, counts = np.unique(self.mask, return_counts=True)
                d = dict(zip(unique, counts))
                if 1.0 in d.keys():
                    vp = 1-(d[1.0]/(self.resolution**2)) #1.0 assigned to in-viz pts
                else:
                    vp = 1
                viz_percent_list.append(vp)
                
                ####MOVIE MADNESS#####
                t_arr, p_arr, d_arr = (self.triptych(), 
                                       self.polarAxes(),
                                       self.diptych())
                lower_set = np.hstack((t_arr, p_arr, d_arr))
                img_arrays.append(lower_set)

                #calc masked M
                #m = self.M_calculation(df, row=index, choice='masked')
                m = self.m if index == 0 else np.dstack((m, self.m))
                masks = self.mask if index == 0 else np.dstack((masks, self.mask))
                maskedmeanM = np.mean(m)
                maskedmeanM_list.append(maskedmeanM)
                #update progress bar
                self.progress.value = self.time
            self.log += 'Complete'
            
            self.log+='\nAdding horizon M/albedo, and viz% to dataframe...'
            df.insert(12, 'maskedmeanM', maskedmeanM_list)
            maskedAlbedo_list = [self.albedo(df, row, choice = 'masked')
                                 for row in range(ncols)]
            df.insert(13, 'maskedAlbedo', maskedAlbedo_list) 
            viz_percent_list = [item*3 for item in viz_percent_list] #norm-ing
            df.insert(14, 'viz_percent', viz_percent_list)
            self.log += 'Complete'
            self.progress.value += 2
              
            self.log += '\nBuilding mp4 frames...'
            img_arrays = [
                np.vstack((self.timeSeries_Plot(df, mx), lower_set))
                for mx, lower_set in enumerate(img_arrays, start=1)
            ]
            self.log += 'Complete'
            self.progress.value += 2
            
            self.log += '\nWriting mp4...'
            self.write_mp4(img_arrays)
            self.log += 'Complete'
            self.progress.value += 2
            
            self.log += '\nWriting dataframe.csv, config.json, & arrays/ to file...'
            self.export_df(df)
            self.dump_json()
            self.export_arrays(m, masks)
            self.log += 'Complete'
            self.progress.value += 2
            
            del (Mp_list, Ap_list, meanM_list, meanAlpha_list, 
                 maskedmeanM_list, maskedAlbedo_list, viz_percent_list, 
                 img_arrays, m, masks)

            self.time = 0
            self.model_dataframe = df
            end_t = time.time()
            run_t = np.around(end_t-start_t, 4)
            cell_t, ar_cs = np.around(run_t/ncols, 4), self.resolution**2
            unique_bins = (len(np.unique(df['bin_assignment'])) 
                           if self.bins!='Max' else ncols) 
            
            self.log+=f"""<pre style="color:lime">\nModel completed in {run_t}s.
            {cell_t}s/timepoint for array of {ar_cs} cells @ {ncols} timepoints
            binned as {unique_bins} azimuths.
            </pre>
            """
            self.progress.value += 2
            self.save_log()
            self.zip_archive()
            
            self.run_counter =+ 1
            self.run_state = False

            return 
        