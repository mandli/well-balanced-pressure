#!/usr/bin/env python

import os

import numpy as np
import matplotlib.pyplot as plt

import clawpack.pyclaw.solution as sol

def load_solution(path, frame=10, y0=0.0):
    # Assumes single grid
    solution = sol.Solution(path=path, frame=frame)
    q = solution.states[0].q
    x = solution.states[0].grid.centers[0]
    y = solution.states[0].grid.centers[1]
    dy = solution.states[0].grid.delta[1]
    index = np.where(abs(y - y0) <= dy / 2.0)[0][0]
    return x, q[:, :, index]


def plot_comparison(base_path, ax, field=3, title=None, 
                                   colors=['red', 'red', 'black', 'black'], 
                                   markers=['o', 'x', 'o', 'x']):

    if title is None:
        title = field

    i = -1
    for split in [True, False]:
        for test_type in ["pressure", "bathymetry"]:
            i += 1
            path = os.path.join(base_path, f"{str(split)[0]}_{test_type}_output")
            x, q = load_solution(path)
            if field < 0:
                values = np.where(q[0, :] >1e-3, q[abs(field), :] / q[0, :], np.zeros(q.shape[1]))
            else:
                values = q[field, :]
            ax.plot(x, values, marker=markers[i], color=colors[i], 
                               markersize=5, 
                               label=f"{str(split)[0]}-{test_type[0]}")

    ax.set_title(f"{title} comparison")
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$q[{}]$".format(field))
    ax.legend()


if __name__ == '__main__':
    base_path = os.path.expandvars(os.path.join("${DATA_PATH}", "split_source"))

    fig, axs = plt.subplots(2, 2)
    fig.set_figwidth(fig.get_figwidth() * 2)
    fig.set_figheight(fig.get_figheight() * 2)
    plot_comparison(base_path, axs[0, 0], field=0, title='Depth')
    plot_comparison(base_path, axs[0, 1], field=3, title='Surface')
    plot_comparison(base_path, axs[1, 0], field=1, title='Momentum')
    plot_comparison(base_path, axs[1, 1], field=-1, title='Velocity')
    fig.savefig("comparison.pdf")
