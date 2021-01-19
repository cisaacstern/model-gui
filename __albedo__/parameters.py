import albedo._albedo.dataset as dataset
#import _albedo.dataset as dataset
import param
import panel as pn
import datetime

class Parameters(dataset.DataSet):
    
    time = param.Selector(default=0, objects=[0,1])
    
    elev     = param.Integer(default=30, bounds=(0, 90), step=5)
    azim     = param.Integer(default=285, bounds=(0, 360), step=15)

    choose3d = param.ListSelector(default=['Pointcloud', 'Planar Fit'],
                                  objects=['Raw Lidar','Pointcloud','Planar Fit'])
    
    resolution = param.Integer(default=30, bounds=(10, 300), step=10)
    sigma      = param.Number(0.5, bounds=(0, 3))
    vertEx     = param.Number(1.0)
    
    set_measurements   = param.ListSelector(
                            default=['Global Up'],
                            objects=['Global Up', 'Direct Dwn', 'Diffuse Dwn'])
    set_planar_curves  = param.ListSelector(
                            default=['M','Alpha'], objects=['M','Alpha','IDR'])
    set_raster_curves  = param.ListSelector(
                            default=[], objects=['M','Alpha','IDR'])
    set_horizon_curves = param.ListSelector(
                            default=['M','Alpha'], objects=['M','Alpha','IDR'])
    set_curve_filler   = param.ListSelector(
                            default=[], 
                            objects=['> Selected M\'s', '> Selected Alpha\'s', 
                                     '> Selected IDR\'s'])
    set_visibile_curve = param.Boolean(True)
    
    activateMask = param.Selector(default='Overlay', objects=['Overlay', 'Remove'])
    
    bins = param.ObjectSelector(default=32,
                                objects=[8, 16, 24, 32, 40, 48, 56, 64, 'Max'])
    
    run = param.Boolean(False)
    
    run_state = param.Boolean(False)
    
    run_counter = param.Integer(0)
    
    log = param.String('')
    
    progress = pn.widgets.Progress(name='Progress', width=450, height=25,
                                   value=0, bar_color='info')
    
    dictionary = param.Dict(default={"default": "dictionary"})
    
    dpi = param.Integer(100)
