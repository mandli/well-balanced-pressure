#!/usr/bin/env python

import os

import numpy as np
import matplotlib.pyplot as plt

import clawpack.pyclaw.solution as sol
import clawpack.geoclaw.surge.plot as surgeplot

def plot_comparison(base_path, ax, y0=0.0, field=3, title=None, 
                                   colors=['red', 'black']):#, markers=['x', 'o']):
    if title is None:
        title = field

    frame = 8
    limits = [np.inf, -np.inf]

    for (i, split) in enumerate([True, False]):
        for ratio in [1, 2]:
            for depth in [500]:
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
                        ax.plot(x, values, color=colors[i], #marker=markers[i],
                                           markersize=5)

                        limits[0] = min(np.min(values), limits[0])
                        limits[1] = max(np.max(values), limits[1])

    ax.set_title(f"{title} comparison")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$q[{}]$".format(field))

    # Load storm track
    track = surgeplot.track_data(os.path.join(path, "fort.track"))
    track_data = track.get_track(frame)
    ax.plot([track_data[0], track_data[0]], limits, 'b--')

    ax.set_ylim(limits)


if __name__ == '__main__':
    base_path = os.path.expandvars(os.path.join("${DATA_PATH}", 
                                                "well-balanced-pressure",
                                                "storm"))

    fig, axs = plt.subplots(2, 2, layout='constrained')
    fig.set_figwidth(fig.get_figwidth() * 2)
    fig.set_figheight(fig.get_figheight() * 2)
    plot_comparison(base_path, axs[0, 0], field=0, title='Depth')
    plot_comparison(base_path, axs[0, 1], field=3, title='Surface')
    plot_comparison(base_path, axs[1, 0], field=1, title='Momentum')
    plot_comparison(base_path, axs[1, 1], field=-1, title='Velocity')
    fig.savefig("comparison.pdf")

    plt.show()