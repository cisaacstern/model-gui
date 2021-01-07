import numpy as np
import matplotlib.pyplot as plt
import _terrain.config as c
from _terrain.topo import Topography

def simple_triptych(filename, grids, bounds, params,
                    figsize=(12,5), dpi=80, wspace=0.05, hspace=0, 
                    left=0.05, right=0.97, top=0.79, bottom=0.1):

    fig, ax = plt.subplots(1,3, figsize=figsize, dpi=dpi)

    ds = filename[:8] #date_string
    R, S = params['R'], params['S']
    line2 = f'\nR, S ={R}, {S}'

    titles = [f'{ds}: Elevation'+line2, f'{ds}: Slope'+line2,
                f'{ds}: Aspect (South=0, East +)'+line2]

    imgs = [grids[0], grids[1], grids[2]]

    cmaps = ['viridis', 'YlOrBr', 'hsv']
    cmap_ranges = [(np.min(imgs[0]), np.max(imgs[0])), (np.min(imgs[1]), np.max(imgs[1])), (-180, 180)]

    ticks = np.linspace(0, params['R']-1, 4)
    
    e_mn, e_mx, n_mn, n_mx, _, _ = bounds 
    xlabels = [str(e_mn)[-2:], str(e_mn+1)[-2:], str(e_mn+2)[-2:], str(e_mx)[-2:]]
    ylabels = [str(n_mn)[-2:], str(n_mn+1)[-2:], str(n_mn+2)[-2:], str(n_mx)[-2:]]

    ims = []
    for i in range(3):
        img, cmap = imgs[i], cmaps[i]
        im = ax[i].imshow(img, origin='lower', cmap=cmap,
                            vmin=cmap_ranges[i][0], vmax=cmap_ranges[i][1])
        ims.append(im)
        ax[i].set_xticks(ticks=ticks)
        ax[i].set_xticklabels(labels=xlabels)
        ax[i].set_yticks(ticks=ticks)
        if i == 0:
            ax[i].set_yticklabels(labels=ylabels)
            ax[i].set_ylabel(f'Northing (+{str(n_mn)[:-2]}e2)')
        else:
            ax[i].set_yticklabels(labels=[])
        if i == 1:
            ax[i].set_xlabel(f'Easting (+{str(e_mn)[:-2]}e2)')
        ax[i].set_aspect("equal")

    plt.subplots_adjust(left=left, right=right, top=top, bottom=bottom, wspace=wspace, hspace=hspace)

    for i in range(3):
        p = ax[i].get_position().get_points().flatten()
        ax_cbar = fig.add_axes([p[0], 0.85, p[2]-p[0], 0.05])
        ax_cbar.set_title(titles[i], loc='left')
        cb = plt.colorbar(ims[i], cax=ax_cbar, orientation='horizontal')
        if i == 2:
            cbar_ticks = [-180, -135, -90, -45, 0, 45, 90, 135, 180]
            cb.set_ticks(cbar_ticks)

    plt.close()
    #plt.show()
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