'''

'''
import codecs

import panel as pn
from panel.template.theme import DarkTheme

from interact import Interact

pn.config.sizing_mode = 'scale_both'

#####
css = '''
.pn-modal-content {
    background-color: #cfcfcf;
    filter: drop-shadow(8px 8px 10px black)
    border: 5px solid white;
}
video {
    width: 100%;
}
.blurred {
  filter: blur(2px) opacity(40%);
}
.bk-root .bk-btn {
    height: 25px;
}
.bk-root .bk-btn-group {
    height: 50px;
}
.bk-root {
    height: inherit;
}
ul {
    height: 50px;
}
span {
    cursor: pointer;
    font-size: x-large;
    text-shadow: 1px 1px 4px purple;
}
'''
pn.config.raw_css.append(css)
#####

react = pn.template.ReactTemplate(title='', theme=DarkTheme)
axis_color = react.theme.bokeh_theme._json['attrs']['Axis']['axis_label_text_color']
canvas_color = '#121212'

# append elements to template & call servable
interact = Interact(axis_color=axis_color, canvas_color=canvas_color)

date = pn.widgets.DiscreteSlider.from_param(interact.param.date)
react.sidebar.append(date)
react.sidebar.append(interact.param.resolution)
react.sidebar.append(interact.param.sigma)
react.sidebar.append(interact.param.bins)
react.sidebar.append(interact.param.time)

##### start working area
toggle = pn.widgets.Toggle(name='Toggle', button_type='success')

@pn.depends(toggle.param.value)
def t(value=toggle.param.value):
    print('Open modal!')
    react.open_modal()
    toggle.param.value = False

react.sidebar.append(toggle)
react.sidebar.append(t)

video = pn.pane.Video('https://file-examples-com.github.io/uploads/2017/04/file_example_MP4_640_3MG.mp4')
react.modal.append(video)
##
js = codecs.open("terrain-corrector/static/custom.js", 'r')
script = pn.pane.HTML(f'<script>{js.read()}</script>')
react.sidebar.append(script)
##
##### end working area

react.sidebar.append(interact.set_terrain)
react.sidebar.append(interact.set_sun)
react.sidebar.append(interact.set_horizons)
react.sidebar.append(interact.set_correction)

gspec = pn.GridSpec(name='Config')
gspec[0, 0:3] = interact.view_terrain
gspec[1, 0:1] = interact.view_sun
gspec[1, 1:3] = interact.view_correction

react.main[:4,:6] = gspec

html_head = codecs.open("terrain-corrector/static/header.html", 'r')
header = pn.pane.HTML(html_head.read())
react.header.append(header)

servable = react.servable()
