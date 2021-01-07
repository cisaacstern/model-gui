import numpy as np
import matplotlib.pyplot as plt
import _terrain.config as c
from _terrain.topo import Topography

def simple_triptych(fn, grids, bounds, params,
                    canvas_color, axis_color,
                    figsize=(12,5), dpi=80, wspace=0.05, hspace=0, 
                    left=0.05, right=0.97, top=0.79, bottom=0.1):
    '''

    '''
    fig, ax = plt.subplots(1,3, figsize=figsize, dpi=dpi)

    #titles are added to the colorbars at the end of this function
    title_date = fn[:4] + '-' + fn[4:6] + '-' + fn[6:8]
    title_line_2 = f'\nR, S ={params["R"]}, {params["S"]}'
    titles = [  
        f'{title_date}: Elevation'+title_line_2,
        f'{title_date}: Slope'+title_line_2,
        f'{title_date}: Aspect (South=0, East +)'+title_line_2
    ]
    cmaps = ['viridis', 'YlOrBr', 'hsv']
    ranges = [(np.min(grids[i]), np.max(grids[i])) for i in range(2)]
    ranges.append((-180, 180))
    ticks = np.linspace(0, params['R']-1, 4)
    
    e_mn, e_mx, n_mn, n_mx, _, _ = bounds
    xlabels = [str(e_mn + i)[-2:] for i in range(4)]
    ylabels = [str(n_mn + i)[-2:] for i in range(4)]

    ims = []
    for i in range(3):
        im = ax[i].imshow(
                grids[i], cmap=cmaps[i], origin='lower',
                vmin=ranges[i][0], vmax=ranges[i][1]
            )
        ims.append(im)
        
        ax[i].set_xticks(ticks=ticks)
        ax[i].set_yticks(ticks=ticks)
        ax[i].set_xticklabels(labels=xlabels)
        ax[i].xaxis.label.set_color(axis_color)
        ax[i].yaxis.label.set_color(axis_color)
        ax[i].tick_params(axis='x', colors=axis_color)
        ax[i].tick_params(axis='y', colors=axis_color)

        if i == 0:
            ax[i].set_yticklabels(labels=ylabels)
            ax[i].set_ylabel(f'Northing (+{str(n_mn)[:-2]}e2)')
        else:
            ax[i].set_yticklabels(labels=[])
            if i == 1:
                ax[i].set_xlabel(f'Easting (+{str(e_mn)[:-2]}e2)')
        ax[i].set_aspect("equal")

    #adjust margins before adding colorbars
    plt.subplots_adjust(left=left, right=right, top=top, bottom=bottom, wspace=wspace, hspace=hspace)

    #add the colorbars
    for i in range(3):
        p = ax[i].get_position().get_points().flatten()
        ax_cbar = fig.add_axes([p[0], 0.85, p[2]-p[0], 0.05])
        ax_cbar.set_title(titles[i], loc='left', color=axis_color)
        ax_cbar.tick_params(axis='x', colors=axis_color)
        cb = plt.colorbar(ims[i], cax=ax_cbar, orientation='horizontal')
        if i == 2:
            cbar_ticks = [-180, -135, -90, -45, 0, 45, 90, 135, 180]
            cb.set_ticks(cbar_ticks)

    fig.patch.set_facecolor(canvas_color)
    plt.close()
    return fig


#TEST AREA
'''
fn = c.TOPO_LIST[-6]
params = {'R': 300, 'S':2.0}

test = Topography(fn)
grids = test.return_grids(params['R'], params['S'])
simple_triptych(filename=fn, grids=grids, 
                bounds=c.BOUNDS, params=params)
'''