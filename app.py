
import terrain.config as c
from terrain.topo import Topography
from terrain.plot import plot_grids

import panel as pn
from panel.template.theme import DarkTheme

pn.extension()
pn.config.sizing_mode = 'scale_both'

react = pn.template.ReactTemplate(title='', theme=DarkTheme)
canvas_color = '#121212'
axis_color = react.theme.bokeh_theme._json['attrs']['Axis']['axis_label_text_color']

#---User controls start here--#
resolution = pn.widgets.IntSlider(name="Resolution", start=10, end=300, value=30)
sigma = pn.widgets.FloatSlider(name="Sigma", start=0.0, end=3.0, value=2) 

@pn.depends(resolution=resolution, sigma=sigma)
def grids(resolution, sigma, date_index=-6, view_fn=plot_grids):
    '''

    '''
    filename = c.TOPO_LIST[date_index]
    params = {'R': resolution, 'S':sigma}

    test = Topography(filename)
    grids = test.return_grids(params['R'], params['S'])
    return view_fn(fn=filename, grids=grids, bounds=c.BOUNDS, params=params,
                    canvas_color=canvas_color, axis_color=axis_color)

# append elements to sidebar
react.sidebar.append(resolution)
react.sidebar.append(sigma)

# Unlike other templates the `ReactTemplate.main` area acts like a GridSpec 
react.main[:4, :6] = grids

# append header
header = pn.pane.HTML(
    """
    <head>
        <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/hack-font@3/build/web/hack-subset.css">
        <style>
            h4 {
                font-family: Hack, monospace;
                display: inline;
            }
            a.txt:link,
            a.txt:visited {
                border-bottom: 1px dashed;
                color: palevioletred;
                font-style: normal;
                font-weight: 400;
                text-decoration: none;
            }
            a.txt:hover,
            a.txt:focus {
                border-bottom-style: solid;
                color: khaki;
                outline: 1px solid;
                outline-offset: .125em;
            }
        </style>
    </head>
    <h4>
        Terrain-Corrector, by 
        <a class="txt" href="http://twitter.com/" target="_blank" >Charles Stern</a>
    </h4>
    <a href="https://twitter.com" target="_blank">
        <img alt="User Guide" src="https://img.shields.io/static/v1?style=plastic&label=User&message=Guide&color=blueviolet">
    </a>
    <a href="https://pradyunsg.me/furo/customisation/" target="_blank">
        <img alt="Blog Posts" src="https://img.shields.io/static/v1?style=plastic&label=Blog&message=Posts&color=green">
    </a>
    <a href="https://github.com/cisaacstern/model-gui" target="_blank">
        <img alt="Github Link" src="https://img.shields.io/static/v1?style=plastic&logo=github&label=View&message=Source&color=yellow">
    </a>
    """
)
react.header.append(header)

react.servable()
