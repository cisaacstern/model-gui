import albedo._albedo.dashcontrols as dashcontrols
#import _albedo.dashcontrols as dashcontrols
import param
import panel as pn
import matplotlib.pyplot as plt
import markdown
import numpy as np
import os
import subprocess
import time

class DashLayout(dashcontrols.DashControls):
    
    def start_session(self):
        '''
        
        '''
        name = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        self.session = name + '_' + str(time.monotonic_ns())
        subprocess.run(['mkdir', f'albedo/exports/{self.session}'])
        return
    
    def return_README(self):
        '''
        
        '''
        with open('albedo/README.md','r') as f:
            html = markdown.markdown(f.read())
        return html
    
    @param.depends('run_state')
    def triptych_dispatch(self):
        if self.run_state == True:
            pass
        else:
            return self.triptych
    
    @param.depends('run_state')
    def dyptich_dispatch(self):
        if self.run_state == True:
            pass
        else:
            return self.diptych
    
    @param.depends('run_state')
    def polar_dispatch(self):
        if self.run_state == True:
            pass
        else:
            return self.polarAxes
            
    @param.depends('run_state')
    def video_dispatch(self):
        s = self.session
        ID = self.ID
        #return video player
        if self.run_state == True:
            pass
        elif self.run_counter == 0:
            return pn.Row('Run model to generate a video record')
        else:
            vid_path = os.path.join(os.getcwd(), 'exports', f'{s}', f'{ID}', 
                                    'outputs', f'{self.ID}.mp4')
                        
            return pn.pane.Video(vid_path, loop=False, width=900)
        
    @param.depends('run_state')
    def download_dispatch(self):
        s = self.session
        ID = self.ID
        #return download button
        if self.run_state == True:
            pass
        elif self.run_counter == 0:
            return pn.Row('Run model to generate a downloadable archive')
        else:
            return pn.widgets.FileDownload(
                file=f'exports/{s}/{ID}.zip',button_type='default',auto=False,
                embed=True)
    
    @param.depends('date')
    def return_time_control(self):
        return pn.Param(
                self.param, parameters=['time'],
                widgets={'time':{'widget_type': pn.widgets.DiscreteSlider, 
                                 'width': 180}},
                         width=200, name='Preview')
    
    @param.depends('dictionary')
    def return_config_dict(self):
        return pn.pane.JSON(self.dictionary, name='JSON', width=300, 
                            theme='dark', depth=2, hover_preview=True)
        
    
    @param.depends('log')
    def return_log_pane(self):
        return pn.pane.HTML(
        f"""
        <div style="overflow-y:scroll;position:relative;bottom:0;height:400px;">
        <pre style="color:white; font-size:12px">Build Log</pre>
        <pre style="color:deepskyblue; font-size:12px">{self.log}</pre>
        </div>
        """,
        style={'background-color':'#000000', 'border':'2px solid black',
               'border-radius': '5px', 'padding': '10px','width':'560px'}
    )
    
    @param.depends('dictionary')
    def reset_run_state(self):
        self.run = False
        self.log = ''
        self.progress.value = 0
        return
    
    @param.depends('run_state', 'dictionary')
    def return_run_button(self):
        args = dict({'width': 80, 'name':'', 'parameters':['run']})
        enabled = pn.Param(
            self.param, **args, 
            widgets={'run':
                     {'widget_type': pn.widgets.Toggle, 'disabled':False},})
        disabled = pn.Param(
            self.param, **args, 
            widgets={'run':
                     {'widget_type': pn.widgets.Toggle, 'disabled':True},})
        if self.progress.value == 0:
            return enabled
        else:
            return disabled
            
    def set_layout(self):
        self.function_row = pn.Row(
            self.set_filename, self.set_dataframe, self.set_raster,
            self.set_axes, self.set_m, self.set_masks, self.run_model, 
            self.reset_run_state, self.update_config
        )
        self.model_tabs = pn.Row(
            pn.Tabs(pn.pane.Markdown(self.return_README(), name='README'),
                    pn.Column(
                        pn.pane.Markdown("""### Configure \nConfigure interactively using these tabs."""),
                        pn.Tabs(
                            pn.Column(
                                pn.Row(self.file_selector, self.pointcloud_control),
                                self.axes3d,
                                name='Date'
                            ),
                            pn.Column(
                                pn.Row(self.raster_control, self.azi_bins,
                                       pn.WidgetBox(self.horizon_preview),
                                       pn.WidgetBox(self.return_time_control)
                                      ),
                                pn.Tabs(
                                    pn.Row(self.triptych_dispatch,
                                           name='Raster Preview',
                                           width=900
                                          ),
                                    pn.Column(pn.Row(self.polar_dispatch, self.dyptich_dispatch),
                                              name='Azimuth Preview',
                                              width=900
                                             )
                                ),
                                name='Raster & Azimuth'
                            ),
                            pn.Column(
                                self.timeseries_control,
                                name='Timeseries'
                            ),
                            pn.Column(
                                'Choose array format: .npy, .mat, .ascii',
                                name='Format',  width=900
                            )
                        ),      
                        name='Configure'
                    ),
                    pn.Column(
                        pn.pane.Markdown(
                            """### Run \nHere's how you run."""
                        ),
                        pn.Row(
                            pn.Column(self.return_config_dict),
                            pn.Column(
                                pn.Row(self.return_run_button, 
                                       pn.Column(pn.Spacer(height=20),
                                                 self.progress)
                                      ),
                                self.return_log_pane
                                )
                        ),
                        name='Run'
                    ),
                    pn.Column(
                        pn.pane.Markdown(
                            """### Export \n Config your output, commit & review, then download."""
                        ),
                        pn.Tabs(
                            pn.Column(
                                self.video_dispatch,
                                name='Review'
                            ),
                            pn.Column(
                                self.download_dispatch,
                                pn.pane.HTML(
                                f'''<pre>
            DATE_CONFIG/
            +--inputs/
            |   +--raw.csv
            |   +--snowsurface.csv
            |   +--radiometers.csv
            +--outputs/
            |   +--config.json
            |   +--build_log.txt
            |   +--animation.mp4
            |   +--dataframe.csv
            |   +--arrays/
            |      +--planar_fit (20, 20, 3)
            |      +--elevation  (?, ?)
            |      +--slope      (?, ?)
            |      +--aspect     (?, ?)
            |      +--M          (?, ?, N)
            |      +--masks      (?, ?, N)
            +
                </pre>
                                '''),
                                name='Download', width=900
                            )
                        ),
                        name='Export'
                    ),
                    active=0,
                    tabs_location='left'
                   ),
        )
        
        plt.close()
        return
        
    def dashboard(self):
        self.start_session()
        self.set_filename()
        self.set_dataframe()
        self.update_config()
        self.set_raster()
        self.set_m()
        self.horizon_package = self.slope2horz()
        self.set_masks()
        self.set_controls()
        self.set_layout()
        return pn.Column(self.function_row,
                         self.model_tabs)