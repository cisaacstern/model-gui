'''

'''
import logging
import codecs

import param
import panel as pn
from panel.template.theme import DarkTheme

from interact import Interact
from static.css import css

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

pn.config.raw_css.append(css)
pn.config.sizing_mode = 'scale_both'

react = pn.template.ReactTemplate(title='', theme=DarkTheme)
axis_color = react.theme.bokeh_theme._json['attrs']['Axis']['axis_label_text_color']
canvas_color = '#121212'

interact = Interact(axis_color=axis_color, canvas_color=canvas_color)

##### start working area
toggle = pn.widgets.Toggle(name='Toggle', button_type='success')

@pn.depends(interact.param.date, interact.param.resolution, 
            interact.param.sigma, interact.param.bins)
def return_modal_content(*args, **kwargs):
    '''
    
    '''
    logger.info('Updating modal content, current_config is %s', interact.current_config)
    content = pn.pane.JSON(interact.current_config)
    return pn.Row(content)

@pn.depends(toggle.param.value)
def open_modal(*args, **kwargs):
    '''

    '''
    logger.debug('Opening modal window.')
    react.open_modal()
    toggle.param.value = False

##### end working area

date = pn.widgets.DiscreteSlider.from_param(interact.param.date)

params = [date, interact.param.resolution, interact.param.sigma, 
            interact.param.bins, interact.param.time]

modal_tools = [toggle, open_modal, interact.update_config]

setter_funcs = [interact.set_terrain, interact.set_sun, 
                interact.set_horizons, interact.set_correction]

sidebar_items = [*params, *modal_tools, *setter_funcs]

for item in sidebar_items:
    react.sidebar.append(item) 

gspec = pn.GridSpec(name='Config', sizing_mode='scale_both')
gspec[0, 0:3] = interact.view_terrain
gspec[1, 0:1] = interact.view_sun
gspec[1, 1:3] = interact.view_correction
react.main[:4,:6] = gspec

html = codecs.open("terrain-corrector/static/header.html", 'r')
html = pn.pane.HTML(html.read())
react.header.append(html)

react.modal.append(return_modal_content)

react.servable()
