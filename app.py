
import _terrain.config as c
from _terrain.topo import Topography
from _terrain.plot import simple_triptych

import panel as pn
from panel.template.theme import DarkTheme
pn.extension()

react = pn.template.ReactTemplate(title='model-gui', theme=DarkTheme)
#canvas = react.theme.bokeh_theme._json['attrs']['ColorBar']['background_fill_color']
canvas = '#121212'
pn.config.sizing_mode = 'scale_both'

#---User controls start here--#
resolution = pn.widgets.IntSlider(name="Resolution", start=10, end=300, value=30)
sigma = pn.widgets.FloatSlider(name="Sigma", start=0.0, end=3.0, value=2) 

@pn.depends(resolution=resolution, sigma=sigma)
def triptych(resolution, sigma, date_index=-6, view_fn=simple_triptych):
    '''

    '''
    filename = c.TOPO_LIST[date_index]
    params = {'R': resolution, 'S':sigma}

    test = Topography(filename)
    grids = test.return_grids(params['R'], params['S'])
    return view_fn(filename=filename, grids=grids, 
                    bounds=c.BOUNDS, params=params)

# append elements to sidebar
react.sidebar.append(resolution)
react.sidebar.append(sigma)

# Unlike other templates the `ReactTemplate.main` area acts like a GridSpec 
react.main[:4, :6] = triptych

react.servable()
