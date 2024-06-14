#!/usr/bin/env python

import os
import sys

import numpy as np
import matplotlib.pyplot as plt

import clawpack.pyclaw.solution as sol
import clawpack.geoclaw.surge.plot as surgeplot

def plot_comparison(base_path, ax, depth, y0=0.0, field=3, limits=None, 
                                          ylabel=None, title=None, 
                                          style=['rx-', 'k-'], legend=False):
    
    frame = 8
    ratio = 1

    compute_limits = False
    if limits is None:
        limits = [np.inf, -np.inf]
        compute_limits = True

    ax.set_title(title)

    plot_item = [None, None]
    item_label = ["split", "non-split"]
    for (i, split) in enumerate([True, False]):
        # Load solution
        path = os.path.join(base_path, f"{str(split)[0]}_n{ratio}_d{abs(depth)}_output")
        solution = sol.Solution(path=path, frame=frame, file_format='binary')
        
        # Plot all states
        for state in solution.states:
            if state.grid.lower[1] <= y0 and y0 <= state.grid.upper[1]:
                x = state.grid.centers[0]
                y = state.grid.centers[1]
                dy = state.grid.delta[1]
                index = np.where(abs(y - y0) <= dy / 2.0)[0][0]
                q = state.q[:, :, index]

                if field < 0:
                    values = np.where(q[0, :] >1e-3, q[abs(field), :] / q[0, :], np.zeros(q.shape[1]))
                else:
                    values = q[field, :]
                plot_item[i], = ax.plot(x, values, style[i], markersize=5, label=item_label[i])


                if compute_limits:
                    limits[0] = min(np.min(values), limits[0])
                    limits[1] = max(np.max(values), limits[1])

    # Plot storm center
    track = surgeplot.track_data(os.path.join(path, "fort.track"))
    track_data = track.get_track(frame)
    ax.plot([track_data[0], track_data[0]], limits, 'b--')

    # Fix up common x-axis
    ax.set_xlim((-500e3, 1000e3))
    ax.set_xlabel(r"$x$ (km)")
    ticks = [-500e3, -250e3, 0.0, 250e3, 500e3, 750e3, 1000e3]
    ax.set_xticks(ticks)
    ax.set_xticklabels([str(int(x/1e3)) for x in ticks])
    ax.grid(True)
    
    # Set y-axis
    ax.set_ylabel(r"$h$ (m)")
    ax.set_ylim(limits)

    if legend:
        ax.legend(loc="upper left", handles=plot_item)

    return ax


if __name__ == '__main__':
    base_path = os.path.expandvars(os.path.join("${DATA_PATH}", 
                                                "well-balanced-pressure",
                                                "storm"))
    if len(sys.argv) > 1:
        depth = int(sys.argv[-1])
        if depth == 100:
            x_mom_limits = (-2, 2.5)
            x_vel_limits = (-0.014, 0.02)
        else:
            x_mom_limits = None
            x_vel_limits = None

    else:
        depth = 500
        x_mom_limits = (-5, 2)
        x_vel_limits = (-0.01, 0.003)

    fig, ax = plt.subplots(1, 1, layout='constrained')
    plot_comparison(base_path, ax, depth, field=0, limits=(depth - 0.25, depth + 1),
                                    title="Depth Comparison", 
                                    ylabel=r"$h$ (m)")
    fig.savefig(f"storm_{depth}_depth.pdf")

    fig, ax = plt.subplots(1, 1, layout='constrained')
    plot_comparison(base_path, ax, depth, field=3, limits=(-0.25, 1), 
                                    title="Surface Comparison", 
                                    ylabel=r"$\eta$ (m)", legend=True)
    fig.savefig(f"storm_{depth}_surface.pdf")
    
    fig, ax = plt.subplots(1, 1, layout='constrained')
    plot_comparison(base_path, ax, depth, field=1, limits=x_mom_limits, 
                                   title="X-Momentum Comparison", 
                                   ylabel=r"$hu$ ($m^2/s$)")
    fig.savefig(f"storm_{depth}_xmomentum.pdf")

    # fig, ax = plt.subplots(1, 1, layout='constrained')
    # plot_comparison(base_path, ax, field=2, limits=None,
    #                                title="Y-Momentum Comparison",   
    #                                ylabel=r"$hv$ ($m^2/s$)")
    # fig.savefig(f"storm_{depth}_ymomentum.pdf")

    fig, ax = plt.subplots(1, 1, layout='constrained')
    plot_comparison(base_path, ax, depth, field=-1,  limits=x_vel_limits, 
                                   title="X-Velocity Comparison", 
                                   ylabel=r"$u$ ($m/s$)")
    fig.savefig(f"storm_{depth}_xvelocity.pdf")

    # fig, ax = plt.subplots(1, 1, layout='constrained')
    # plot_comparison(base_path, ax, field=-2,  limits=None, 
    #                                title="Y-Velocity Comparison", 
    #                                ylabel=r"$v$ ($m/s$)")
    # fig.savefig(f"storm_{depth}_yvelocity.pdf")

    # plt.show()