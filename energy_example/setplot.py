#!/usr/bin/env python

import os

import numpy as np
import matplotlib.pyplot as plt
import datetime

import clawpack.visclaw.colormaps as colormap
import clawpack.visclaw.gaugetools as gaugetools
import clawpack.clawutil.data as clawutil
import clawpack.amrclaw.data as amrclaw
import clawpack.geoclaw.data as geodata


import clawpack.geoclaw.surge.plot as surgeplot

# Run Setup
R_m = 10e3
d = 40.0
g = 9.81
rho = 1025
Fr = 1.0
U = Fr * np.sqrt(g * d)

# Set indices
surgeplot.wind_field = 2
surgeplot.pressure_field = 4

try:
    from setplotfg import setplotfg
except:
    setplotfg = None

def setplot(plotdata=None):
    """"""

    if plotdata is None:
        from clawpack.visclaw.data import ClawPlotData
        plotdata = ClawPlotData()

    # clear any old figures,axes,items data
    plotdata.clearfigures()
    plotdata.format = 'ascii'

    # Load data from output
    clawdata = clawutil.ClawInputData(2)
    clawdata.read(os.path.join(plotdata.outdir, 'claw.data'))
    physics = geodata.GeoClawData()
    physics.read(os.path.join(plotdata.outdir, 'geoclaw.data'))
    surge_data = geodata.SurgeData()
    surge_data.read(os.path.join(plotdata.outdir, 'surge.data'))
    friction_data = geodata.FrictionData()
    friction_data.read(os.path.join(plotdata.outdir, 'friction.data'))

    # Load storm track
    track = surgeplot.track_data(os.path.join(plotdata.outdir, 'fort.track'))

    # Set afteraxes function
    def surge_afteraxes(cd):
        surgeplot.surge_afteraxes(cd, track, plot_direction=False,
                                             kwargs={"markersize": 4})

    # Color limits
    surface_limits = [-0.05, 0.05]
    speed_limits = [-0.03, 0.03]
    wind_limits = [0, 64]
    pressure_limits = [1005, 1015]
    friction_bounds = [0.01, 0.04]

    def friction_after_axes(cd):
        plt.title(r"Manning's $n$ Coefficient")

    def draw_bounding_box(cd):
        ax = plt.gca()
        print(cd.t, U)
        ax.plot((-R_m + U * cd.t, -R_m + U * cd.t, R_m + U * cd.t, R_m + U * cd.t, -R_m + U * cd.t), (-R_m, R_m, R_m, -R_m, -R_m), 'k--')

    # ==========================================================================
    #   Plot specifications
    # ==========================================================================
    # Surface Figure
    plotfigure = plotdata.new_plotfigure(name="Surface")
    plotfigure.kwargs = {"figsize": (6.4 * 6, 4.8)}
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = "Surface"
    plotaxes.scaled = False
    plotaxes.xlimits = (clawdata.lower[0], clawdata.upper[0])
    plotaxes.ylimits = (clawdata.lower[1], clawdata.upper[1])
    plotaxes.afteraxes = draw_bounding_box

    surgeplot.add_surface_elevation(plotaxes, bounds=surface_limits)
    surgeplot.add_land(plotaxes, bounds=[0.0, 20.0])
    # plotaxes.plotitem_dict['surface'].amr_patchedges_show = [0] * 10
    plotaxes.plotitem_dict['land'].amr_patchedges_show = [0] * 10

    # Speed Figure
    plotfigure = plotdata.new_plotfigure(name="Currents")
    # plotfigure.kwargs = {"figsize": (6.4 * 2, 4.8)}
    plotfigure.show = True
    plotaxes.scaled = True
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = "Currents"
    plotaxes.xlimits = (clawdata.lower[0], clawdata.upper[0])
    plotaxes.ylimits = (clawdata.lower[1], clawdata.upper[1])
    plotaxes.afteraxes = draw_bounding_box

    surgeplot.add_speed(plotaxes, bounds=[0.0, speed_limits[1]])
    surgeplot.add_land(plotaxes, bounds=[0.0, 20.0])
    plotaxes.plotitem_dict['speed'].amr_patchedges_show = [0] * 10
    plotaxes.plotitem_dict['land'].amr_patchedges_show = [0] * 10

    # Pressure field
    plotfigure = plotdata.new_plotfigure(name='Pressure')
    plotfigure.show = surge_data.pressure_forcing and True

    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlimits = (clawdata.lower[0], clawdata.upper[0])
    plotaxes.ylimits = (clawdata.lower[1], clawdata.upper[1])
    plotaxes.title = "Pressure Field"
    plotaxes.afteraxes = draw_bounding_box
    plotaxes.scaled = True
    surgeplot.add_pressure(plotaxes, bounds=pressure_limits)
    surgeplot.add_land(plotaxes, bounds=[0.0, 20.0])

    # ========================================================================
    # Transects
    def compute_max(current_data, field=3, title=r"$\max |\eta|= {}$"):
        if field == 3:
            max_value = np.max(np.abs(current_data.q[field, :, :]))
        else:
            h = current_data.q[0, :, :]
            u = np.where(h > 1e-3, current_data.q[field, :, :] / h, np.zeros(h.shape))
            max_value = np.max(np.abs(u))

        ax = plt.gca()
        ax.set_title(title.format(max_value))
        if field == 1 or field == 2:
            ax.legend([r'$u$', r"$v$"])

    def time_title(cd, title_prefix, T_0, legend=False):
        ax = plt.gca()
        ax.set_title(r"{} at $t / T_0 = {}$".format(title_prefix, cd.t / T_0))
        if legend:
            ax.legend([r'$u$', r"$v$"])


    def transect_velocity(current_data, field, y0=0.0):
        y = current_data.y
        dy = current_data.dy
        index = np.where(abs(y - y0) <= dy / 2.0)[1][0]
        x = current_data.x[:, index]

        h = current_data.q[0, :, index]
        hu = current_data.q[1, :, index]
        hv = current_data.q[2, :, index]
        if field == 1:
            return x, np.where(h > 1e-3, hu / h, np.zeros(h.shape))
        else:
            return x, np.where(h > 1e-3, hv / h, np.zeros(h.shape))

    def transect_eta(current_data, y0=0.0, eta_0=0.04):
        y = current_data.y
        dy = current_data.dy
        index = np.where(abs(y - y0) <= dy / 2.0)[1][0]
        x = current_data.x[:, index]

        h = current_data.q[0, :, index]
        return x, current_data.q[3, :, index] / eta_0

    # === Surface ===
    plotfigure = plotdata.new_plotfigure(name="Surface Transect")
    plotfigure.show = True
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = "Surface"
    plotaxes.xlabel = "x (m)"
    plotaxes.ylabel = r"$\eta / \eta_0$"
    plotaxes.xlimits = [clawdata.lower[0], clawdata.upper[0]]
    # plotaxes.ylimits = [-0.02, 0.05]
    plotaxes.grid = True

    plotaxes.afteraxes = lambda t: time_title(t, r"$\eta / \eta_0$", T_0)
    # plotaxes.afteraxes = lambda cd: compute_max(cd, 
    #                             title=r"$\eta / \eta_0$ Transect - $\max |\eta| = {}$")

    # === Velocity ===
    plotfigure = plotdata.new_plotfigure(name="Velocity X Transect")
    plotfigure.show = True
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.xlabel = "x (m)"
    plotaxes.ylabel = r"$u, v$"
    plotaxes.xlimits = [clawdata.lower[0], clawdata.upper[0]]
    plotaxes.ylimits = speed_limits
    plotaxes.grid = True
    plotaxes.afteraxes = lambda cd: time_title(cd, r"$u, v$", T_0, legend=True)
    plotitem = plotaxes.new_plotitem(plot_type="1d_from_2d_data")
    plotitem.map_2d_to_1d = lambda cd: transect_velocity(cd, 1)
    plotitem.plotstyle = 'bx-'
    plotitem.kwargs = {"markersize": 3}
    plotitem = plotaxes.new_plotitem(plot_type="1d_from_2d_data")
    plotitem.map_2d_to_1d = lambda cd: transect_velocity(cd, 2)
    plotitem.plotstyle = 'kx-'
    plotitem.kwargs = {"markersize": 3}

    # ========================================================================
    #  Figures for gauges
    # ==========================================================================
    plotfigure = plotdata.new_plotfigure(name='Gauge Surfaces', figno=300,
                                         type='each_gauge')
    plotfigure.show = True
    plotfigure.clf_each_gauge = True

    plotaxes = plotfigure.new_plotaxes()
    T_0 = R_m / np.sqrt(9.81 * d)
    plotaxes.time_scale = 1 / T_0
    plotaxes.grid = True
    plotaxes.xlimits = 'auto'
    plotaxes.ylimits = 'auto'
    plotaxes.title = "Surface"
    plotaxes.ylabel = "Surface (m)"
    plotaxes.time_label = r"$t / T_0$ (s)"

    plotitem = plotaxes.new_plotitem(plot_type='1d_plot')
    plotitem.plot_var = surgeplot.gauge_surface

    #  Gauge Location Plot
    def gauge_location_afteraxes(cd):
        plt.subplots_adjust(left=0.12, bottom=0.06, right=0.97, top=0.97)
        surge_afteraxes(cd)
        gaugetools.plot_gauge_locations(cd.plotdata, gaugenos='all',
                                        format_string='ko', add_labels=True)

    #
    #  Gauge Location Plot
    #
    def gauge_location_afteraxes(cd):
        plt.subplots_adjust(left=0.12, bottom=0.06, right=0.97, top=0.97)
        surge_afteraxes(cd)
        gaugetools.plot_gauge_locations(cd.plotdata, gaugenos='all',
                                        format_string='bx', add_labels=False)
        gaugetools.plot_gauge_locations(cd.plotdata, gaugenos=[0, 11, 22, 10, 21, 32],
                                        format_string='ko', add_labels=True)

    plotfigure = plotdata.new_plotfigure(name="Gauge Locations")
    plotfigure.show = False

    # Set up for axes in this figure:
    plotaxes = plotfigure.new_plotaxes()
    plotaxes.title = 'Gauge Locations'
    plotaxes.scaled = True
    plotaxes.xlimits = (clawdata.lower[0], clawdata.upper[0])
    plotaxes.ylimits = (clawdata.lower[1], clawdata.upper[1])
    plotaxes.afteraxes = gauge_location_afteraxes
    surgeplot.add_surface_elevation(plotaxes, bounds=surface_limits)
    surgeplot.add_land(plotaxes, bounds=[0.0, 20.0])
    plotaxes.plotitem_dict['surface'].amr_patchedges_show = [0] * 10
    plotaxes.plotitem_dict['land'].amr_patchedges_show = [0] * 10

    # -----------------------------------------
    # Parameters used only when creating html and/or latex hardcopy
    # e.g., via pyclaw.plotters.frametools.printframes:

    plotdata.printfigs = True                # print figures
    plotdata.print_format = 'png'            # file format
    plotdata.print_framenos = 'all'          # list of frames to print
    # plotdata.print_gaugenos = 'all'        # list of gauges to print
    plotdata.print_gaugenos = [10, 21, 32]   # list of gauges to print
    plotdata.print_fignos = 'all'            # list of figures to print
    plotdata.html = True                     # create html files of plots?
    plotdata.latex = True                    # create latex file of plots?
    plotdata.latex_figsperline = 2           # layout of plots
    plotdata.latex_framesperline = 1         # layout of plots
    plotdata.latex_makepdf = False           # also run pdflatex?
    plotdata.parallel = True                 # parallel plotting

    return plotdata
