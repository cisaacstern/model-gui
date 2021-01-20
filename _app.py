import codecs

import param
import panel as pn
from panel.template.theme import DarkTheme

import terrain.config as c
from terrain.topo import Topography
from terrain.plot import plot_grids

pn.extension()
pn.config.sizing_mode = 'scale_both'

react = pn.template.ReactTemplate(title='', theme=DarkTheme)
canvas_color = '#121212'
axis_color = react.theme.bokeh_theme._json['attrs']['Axis']['axis_label_text_color']

#---User controls start here--#

date = pn.widgets.DiscreteSlider(name="Date", options=c.DATE_DICT, value=68)

resolution = pn.widgets.IntSlider(name="Resolution", start=10, end=300, value=150)
sigma = pn.widgets.FloatSlider(name="Sigma", start=0.0, end=3.0, value=1) 

#---plot function--#
@pn.depends(resolution=resolution, sigma=sigma, date=date)
def grids(resolution, sigma, date=date, view_fn=plot_grids):
    '''

    '''
    filename = c.TOPO_LIST[date]
    params = {'R': resolution, 'S':sigma}

    test = Topography(filename)
    grids = test.return_grids(params['R'], params['S'])
    return view_fn(fn=filename, grids=grids, bounds=c.BOUNDS, params=params,
                    canvas_color=canvas_color, axis_color=axis_color)

#--- New work below here 

class Interact(param.Parameterized):

    nums = list(c.DATE_DICT.values())
    print(nums)
    date = param.Selector(default=70, objects=nums)
    resolution = param.Integer(150, bounds=(10, 300))
    sigma = param.Number(1.0, bounds=(0.0, 3.0))

    @param.depends('date', 'resolution', 'sigma')
    def grids(self, view_fn=plot_grids):
        '''

        '''
        filename = c.TOPO_LIST[self.date]
        params = {'R': self.resolution, 'S': self.sigma}

        test = Topography(filename)
        grids = test.return_grids(params['R'], params['S'])
        return view_fn(fn=filename, grids=grids, bounds=c.BOUNDS, params=params,
                        canvas_color=canvas_color, axis_color=axis_color)

    


# append elements to template

'''
react.sidebar.append(date)
react.sidebar.append(resolution)
react.sidebar.append(sigma)

react.main[:4, :6] = grids
'''

interact = Interact()
react.sidebar.append(interact.param)
react.main[:4, :6] = interact.grids

html_head = codecs.open("terrain-corrector/static/header.html", 'r')
header = pn.pane.HTML(html_head.read())
react.header.append(header)

# define servable
servable = react.servable()
