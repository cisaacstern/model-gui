'''
This module defines static functions for plotting.
'''

import numpy as np
import matplotlib.pyplot as plt
import terrain.config as c


def generate_titles(fn, params, _type):
    '''

    '''
    assert (_type in ('topo', 'time'), 
        f'_type must be one of \'topo\' or \'time\', got f{_type}')

    title_date = fn[:4] + '-' + fn[4:6] + '-' + fn[6:8]
    title_line_2 = f'\nR, S, B ={params["R"]}, {params["S"]}, {params["B"]}'

    if _type == 'topo':
        titles = [  
            f'{title_date}: Elevation'+title_line_2,
            f'{title_date}: Slope'+title_line_2,
            f'{title_date}: Aspect (South=0, East +)'+title_line_2
        ]
    elif _type == 'time':
        titles = [
            f'{title_date}: Terrain Correction' + title_line_2,
            f'{title_date}: Current Obsruction' + title_line_2
        ]

    return titles

def plot_grids(grids, titles, params, cmaps, d, 
                axis_color, canvas_color):
    '''

    '''
    plt.close('all')

    _len = len(grids)
    iterables = [grids, titles, cmaps]
    for i in range(len(iterables)):
        arg = iterables[i]
        assert len(arg) == _len, f'{arg} length not {_len}.'

    fig, ax = plt.subplots(1, _len, figsize=d['figsize'], dpi=d['dpi'])

    ranges = [(np.min(grids[i]), np.max(grids[i])) for i in range(_len-1)]
    ranges.append((-180, 180))

    ticks = np.linspace(0, params['R']-1, 4)
    xlabels = [str(c.EAST_MIN + i)[-2:] for i in range(4)]
    ylabels = [str(c.NORTH_MIN + i)[-2:] for i in range(4)]

    ims = []
    for i in range(_len):
        im = ax[i].imshow(
                X = grids[i],
                cmap = cmaps[i], 
                vmin=ranges[i][0], vmax=ranges[i][1],
                origin='lower'
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
            ax[i].set_ylabel(f'Northing (+{str(c.NORTH_MIN)[:-2]}e2)')
        else:
            ax[i].set_yticklabels(labels=[])
            if i == 1:
                ax[i].set_xlabel(f'Easting (+{str(c.EAST_MIN)[:-2]}e2)')
        ax[i].set_aspect("equal")

    plt.subplots_adjust(left=d['left'], right=d['right'], top=d['top'], 
                        bottom=d['bottom'], wspace=d['wspace'], hspace=d['hspace'])
    
    for i in range(_len):
        p = ax[i].get_position().get_points().flatten()
        ax_cbar = fig.add_axes([p[0], 0.85, p[2]-p[0], 0.05])
        ax_cbar.set_title(titles[i], loc='left', color=axis_color)
        ax_cbar.tick_params(axis='x', colors=axis_color)
        cb = plt.colorbar(ims[i], cax=ax_cbar, orientation='horizontal')
        if i == 2:
            cbar_ticks = [-180, -135, -90, -45, 0, 45, 90, 135, 180]
            cb.set_ticks(cbar_ticks)

    fig.patch.set_facecolor(canvas_color)

    return fig


def plot_sun(df, angle_dict, time, bins, canvas_color, axis_color, d):
    '''

    '''
    plt.close('all')
    
    fig = plt.figure(figsize=d['figsize'], dpi=d['dpi'])

    tks = [np.deg2rad(a) for a in np.linspace(0,360,8,endpoint=False)]
    xlbls = np.array(['N','45','E','135','S','225','W','315'])

    ax = fig.add_subplot(111, projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_xticks((tks))
    ax.set_xticklabels(xlbls, rotation="vertical", size=12)
    ax.tick_params(axis='x', pad = 0.5)
    ax.set_theta_direction(-1)
    ax.set_rmin(0)
    ax.set_rmax(90)
    ax.set_rlabel_position(90)
    ax.set_facecolor(canvas_color)
    ax.spines['polar'].set_color(axis_color)
    ax.xaxis.label.set_color(axis_color)
    ax.yaxis.label.set_color(axis_color)
    ax.tick_params(axis='x', colors=axis_color)
    ax.tick_params(axis='y', colors=axis_color)
    
    col = df['bin_assignment']
    xs = [np.deg2rad(angle_dict[entry]) for entry in col]
    x  = np.deg2rad(angle_dict[col.iloc[time]])
    ys = df['solar_altitude']
    y  = df['solar_altitude'].iloc[time]

    ax.scatter(xs,ys, s=10, c='orange',alpha=0.5)
    ax.scatter(x, y, s=500, c='gold',alpha=1)
    
    date = df['MeasDateTime'].iloc[time]
    line1=f'{date} Sun Position'
    line2=f'Azi, SZA={np.around((np.rad2deg(x),y),1)}, Bins={bins}'

    plt.subplots_adjust(top=d['top'], bottom=d['bottom'], 
                        left=d['left'], right=d['right'])

    p = ax.get_position().get_points().flatten()
    ax_cbar = fig.add_axes([p[0]+0.085, 0.85, p[2]-p[0], 0.05])
    ax_cbar.set_title(line1+'\n'+line2, loc='left', color=axis_color)
    ax_cbar.axis('off')

    fig.patch.set_facecolor(canvas_color)
    return fig
