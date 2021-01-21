'''

'''
import codecs

import param
import panel as pn
from panel.template.theme import DarkTheme

import terrain.config as c
from terrain.topo import Topography
from terrain.time import TimeSeries
from terrain.params import Correction, Horizon
from terrain.plot import plot_grids, generate_titles, plot_sun

pn.extension()
pn.config.sizing_mode = 'scale_both'

react = pn.template.ReactTemplate(title='', theme=DarkTheme)
canvas_color = '#121212'
axis_color = react.theme.bokeh_theme._json['attrs']['Axis']['axis_label_text_color']

class Interact(param.Parameterized):
    '''
    A paramaterized classed in the mold of Panel example.
    '''
    #---parameters---#
    nums = list(c.DATE_DICT.values()) #update this
    date = param.Selector(default=70, objects=nums)
    resolution = param.Integer(150, bounds=(10, 300), step=10)
    sigma = param.Number(1.0, bounds=(0.0, 3.0))
    bins = param.Integer(32, bounds=(8,64), step=8)
    #---preview controls---#
    time = param.Integer(5, bounds=(0,100)) #needs regen each time 

    def set_view_attributes(self):
        '''
        Instance method for resetting key attributes.
        Note that though this is called from within self.view_grids(),
        it deliberately sets instance variables.
        '''
        self.fname = c.TOPO_LIST[self.date]
        self.params = {'R':self.resolution, 'S':self.sigma, 'B':self.bins}

        test = Topography(self.fname)
        self.grids = test.return_grids(self.params['R'], self.params['S'])

    @param.depends('date', 'resolution', 'sigma')#, 'time')
    def view_terrain(self, view_fn=plot_grids):
        '''
        Two key functions here: (a) sets view attributes; and (b) serves
        the grid plot. dims are variablized because that depends.
        '''
        self.set_view_attributes()
        titles = generate_titles(fn=self.fname, params=self.params, _type='topo')
        cmaps = ['viridis', 'YlOrBr', 'hsv']
        dims = {'figsize':(12,5), 'dpi':80, 'wspace':0.05, 'hspace':0, 
                'left':0.05, 'right':0.97, 'top':0.79, 'bottom':0.1}

        return view_fn(grids=self.grids, params=self.params, titles=titles, 
                        cmaps=cmaps, d=dims, axis_color=axis_color, canvas_color=canvas_color)


    @param.depends('date', 'bins', 'time')
    def view_sun(self, view_fn=plot_sun):
        '''

        '''
        ts = TimeSeries(self.date)
        self.df = ts.reassign_bins(self.bins, ts.df)
        _dict = ts.generate_angle_dict(self.bins)

        dims = {'figsize':(4,5), 'top':1, 'bottom':0, 'left':0.2, 'right':0.95}

        return view_fn(df=self.df, angle_dict=_dict, time=self.time, bins=self.bins,
                        canvas_color=canvas_color, axis_color=axis_color, d=dims)

    @param.depends('date', 'resolution', 'sigma', 'bins', 'time')#'obscure', 
    def view_correction(self, view_fn=plot_grids):
        '''
        
        For more information on these algorithms, see docstrings in source.
        '''
        slope_and_aspect_grids = self.grids[1:]
        corr = Correction()
        corr_array = corr.calculate_correction(
            grids=slope_and_aspect_grids, 
            df=self.df,
            time=self.time
        )

        titles = generate_titles(fn=self.fname, params=self.params, _type='time')
        cmaps = ['magma', 'binary']
        dims = {'figsize':(8,5), 'dpi':80, 'wspace':0.1, 'hspace':0, 
                'top':0.85, 'bottom':0.05, 'left':0.095, 'right':0.95}

        # corr_horizon_array = corr.calculate_horizons
        grids = [corr_array, self.grids[0]] 
        return view_fn(grids=grids, params=self.params, titles=titles, 
                        cmaps=cmaps, d=dims, axis_color=axis_color, canvas_color=canvas_color)

    def run_model(self):
        # can i call the same functions?
        pass

# append elements to template & call servable
interact = Interact()
react.sidebar.append(interact.param)
react.main[0:2, 0:6] = interact.view_terrain
react.main[2:4, 0:2] = interact.view_sun
react.main[2:4, 2:6] = interact.view_correction

html_head = codecs.open("terrain-corrector/static/header.html", 'r')
header = pn.pane.HTML(html_head.read())
react.header.append(header)

servable = react.servable()
