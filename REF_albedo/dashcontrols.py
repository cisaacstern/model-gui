import albedo._albedo.runmodel as runmodel
#import _albedo.runmodel as runmodel
import panel as pn

class DashControls(runmodel.RunModel):

    def set_controls(self):
        self.file_selector = pn.WidgetBox(
            pn.Param(self.param, parameters=['date'], 
                     widgets={'date':{'widget_type': pn.widgets.DiscreteSlider, 
                                      'width': 180}},
                     width=200, name='File'
                    )
        )
        self.pointcloud_control = pn.WidgetBox(
            pn.Row(
                pn.Param(self.param, parameters=['choose3d'], 
                     widgets={'choose3d':
                              {'widget_type': pn.widgets.CheckBoxGroup, 
                               'inline': False}},
                     width=100, name='View'
                    ),
                pn.Param(self.param, parameters=['elev'], 
                     widgets={'elev':
                              {'widget_type': pn.widgets.IntSlider, 
                                      'width': 80}},
                     width=100, name=''
                    )
            )
        )
        self.raster_control = pn.WidgetBox(
            pn.Row(
                pn.Param(self.param, parameters=['resolution'],
                     width=100, name='Raster'),
                pn.Param(self.param, parameters=['sigma'],
                     width=100, name='')
            )
        )
        self.azi_bins = pn.WidgetBox(
            pn.Param(self.param, parameters=['bins'],
                     widgets={'bins':{'widget_type': pn.widgets.DiscreteSlider,
                                      'width':87}}, 
                     width=107, name='Azimuth')
        )
        self.horizon_preview = pn.Param(
            self.param, parameters=['activateMask'],
            widgets={'activateMask':{'widget_type': pn.widgets.RadioBoxGroup,
                                     'inline': False}}, 
            name='Shadows', width=105
        )
        m = pn.Param(
            self.param, parameters=['set_measurements'], 
            widgets={'set_measurements':{'widget_type':pn.widgets.CheckBoxGroup,
                                          'inline': False, 'width': 110,
                                          'name': 'Measurements'}
                    },
            name='Measurements', width=110
        )
        p = pn.Param(
            self.param, parameters=['set_planar_curves'], 
            widgets={'set_planar_curves':{'widget_type':pn.widgets.CheckBoxGroup,
                                          'inline': False, 'width': 70,
                                          'name': 'Planar'}
                    },
            name='Planar', width=70
        )
        r = pn.Param(
            self.param, parameters=['set_raster_curves'], 
            widgets={'set_raster_curves':{'widget_type':pn.widgets.CheckBoxGroup,
                                          'inline': False, 'width': 70,
                                          'name': 'Raster'}
                    },
            name='Raster', width=70
        )
        h = pn.Param(
            self.param, parameters=['set_horizon_curves'], 
            widgets={'set_horizon_curves':{'widget_type':pn.widgets.CheckBoxGroup,
                                          'inline': False, 'width': 70,
                                          'name': 'Horizon'}
                    },
            name='Horizon', width=70
        )
        f = pn.Param(
            self.param, parameters=['set_curve_filler'], 
            widgets={'set_curve_filler':{'widget_type':pn.widgets.CheckBoxGroup,
                                          'inline': False, 'width': 140,
                                          'name': 'Fill between'}
                    },
            name='Fill between', width=140
        )
        v = pn.Param(
            self.param, parameters=['set_visibile_curve'], 
            widgets={'set_visibile_curve':{'widget_type':pn.widgets.Checkbox,
                                          'width': 70, 
                                          'name': 'Viz % Curve'}
                    },
            name='_', width=80
        )
        self.timeseries_control = pn.WidgetBox(
            pn.Row(m, p, r, h, f, v), 
            width=645, height=100
        )

        return