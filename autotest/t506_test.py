"""
Disv and Disu unstructured grid tests using gridgen and the underlying
flopy.discretization grid classes

"""

import os
import platform
import numpy as np

try:
    from shapely.geometry import Polygon
except ImportWarning as e:
    print("Shapely not installed, tests cannot be run.")
    Polygon = None


import flopy
from flopy.utils.gridgen import Gridgen

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.collections import QuadMesh, PathCollection, LineCollection
except:
    print("Matplotlib not installed, tests cannot be run.")
    matplotlib = None
    plt = None

from ci_framework import baseTestDir, flopyTest

# Set gridgen executable
gridgen_exe = "gridgen"
if platform.system() in "Windows":
    gridgen_exe += ".exe"
gridgen_exe = flopy.which(gridgen_exe)

# set mf6 executable
mf6_exe = "mf6"
if platform.system() in "Windows":
    mf6_exe += ".exe"
mf6_exe = flopy.which(mf6_exe)

# set mfusg executable
mfusg_exe = "mfusg"
if platform.system() in "Windows":
    mfusg_exe += ".exe"
mfusg_exe = flopy.which(mfusg_exe)

baseDir = baseTestDir(__file__, relPath="temp", verbose=True)

VERBOSITY_LEVEL = 0


def test_mf6disv():

    if gridgen_exe is None:
        print(
            "Unable to run test_mf6disv(). Gridgen executable not available."
        )
        return

    if Polygon is None:
        print("Unable to run test_mf6disv(). shapely is not available.")
        return

    # set up a gridgen workspace
    gridgen_ws = f"{baseDir}_mf6disv"
    testFramework = flopyTest(verbose=True, testDirs=gridgen_ws, create=True)

    name = "dummy"
    nlay = 3
    nrow = 10
    ncol = 10
    delr = delc = 1.0
    top = 1
    bot = 0
    dz = (top - bot) / nlay
    botm = [top - k * dz for k in range(1, nlay + 1)]

    # Create a dummy model and regular grid to use as the base grid for gridgen
    sim = flopy.mf6.MFSimulation(
        sim_name=name, sim_ws=gridgen_ws, exe_name="mf6"
    )
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name)

    dis = flopy.mf6.ModflowGwfdis(
        gwf,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
    )

    # Create and build the gridgen model with a refined area in the middle
    g = Gridgen(dis, model_ws=gridgen_ws)
    polys = [Polygon([(4, 4), (6, 4), (6, 6), (4, 6)])]
    g.add_refinement_features(polys, "polygon", 3, range(nlay))
    g.build()
    disv_gridprops = g.get_gridprops_disv()

    # find the cell numbers for constant heads
    chdspd = []
    ilay = 0
    for x, y, head in [(0, 10, 1.0), (10, 0, 0.0)]:
        ra = g.intersect([(x, y)], "point", ilay)
        ic = ra["nodenumber"][0]
        chdspd.append([(ilay, ic), head])

    # build run and post-process the MODFLOW 6 model
    name = "mymodel"
    sim = flopy.mf6.MFSimulation(
        sim_name=name,
        sim_ws=gridgen_ws,
        exe_name="mf6",
        verbosity_level=VERBOSITY_LEVEL,
    )
    tdis = flopy.mf6.ModflowTdis(sim)
    ims = flopy.mf6.ModflowIms(sim, linear_acceleration="bicgstab")
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name, save_flows=True)
    disv = flopy.mf6.ModflowGwfdisv(gwf, **disv_gridprops)
    ic = flopy.mf6.ModflowGwfic(gwf)
    npf = flopy.mf6.ModflowGwfnpf(
        gwf, xt3doptions=True, save_specific_discharge=True
    )
    chd = flopy.mf6.ModflowGwfchd(gwf, stress_period_data=chdspd)
    budget_file = f"{name}.bud"
    head_file = f"{name}.hds"
    oc = flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    )
    sim.write_simulation()

    gwf.modelgrid.set_coord_info(angrot=15)

    # write grid and model shapefiles
    fname = os.path.join(gridgen_ws, "grid.shp")
    gwf.modelgrid.write_shapefile(fname)
    fname = os.path.join(gridgen_ws, "model.shp")
    gwf.export(fname)

    if mf6_exe is not None:
        sim.run_simulation(silent=True)
        head = gwf.output.head().get_data()
        bud = gwf.output.budget()
        spdis = bud.get_data(text="DATA-SPDIS")[0]
        if matplotlib is not None:
            f = plt.figure(figsize=(10, 10))
            vmin = head.min()
            vmax = head.max()
            for ilay in range(gwf.modelgrid.nlay):
                ax = plt.subplot(1, gwf.modelgrid.nlay, ilay + 1)
                pmv = flopy.plot.PlotMapView(gwf, layer=ilay, ax=ax)
                ax.set_aspect("equal")
                pmv.plot_array(
                    head.flatten(), cmap="jet", vmin=vmin, vmax=vmax
                )
                pmv.plot_grid(colors="k", alpha=0.1)
                pmv.contour_array(
                    head,
                    levels=[0.2, 0.4, 0.6, 0.8],
                    linewidths=3.0,
                    vmin=vmin,
                    vmax=vmax,
                )
                ax.set_title(f"Layer {ilay + 1}")
                pmv.plot_vector(spdis["qx"], spdis["qy"], color="white")
            fname = "results.png"
            fname = os.path.join(gridgen_ws, fname)
            plt.savefig(fname)
            plt.close("all")

        # test plotting
        disv_dot_plot(gridgen_ws)

    return


def test_mf6disu():
    # set up a gridgen workspace
    gridgen_ws = f"{baseDir}_mf6disu"
    testFramework = flopyTest(verbose=True, testDirs=gridgen_ws, create=True)

    name = "dummy"
    nlay = 3
    nrow = 10
    ncol = 10
    delr = delc = 1.0
    top = 1
    bot = 0
    dz = (top - bot) / nlay
    botm = [top - k * dz for k in range(1, nlay + 1)]

    # Create a dummy model and regular grid to use as the base grid for gridgen
    sim = flopy.mf6.MFSimulation(
        sim_name=name, sim_ws=gridgen_ws, exe_name="mf6"
    )
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name)

    dis = flopy.mf6.ModflowGwfdis(
        gwf,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
    )

    # Create and build the gridgen model with a refined area in the middle
    g = Gridgen(dis, model_ws=gridgen_ws)
    polys = [Polygon([(4, 4), (6, 4), (6, 6), (4, 6)])]
    g.add_refinement_features(polys, "polygon", 3, layers=[0])
    g.build()
    disu_gridprops = g.get_gridprops_disu6()

    chdspd = []
    for x, y, head in [(0, 10, 1.0), (10, 0, 0.0)]:
        ra = g.intersect([(x, y)], "point", 0)
        ic = ra["nodenumber"][0]
        chdspd.append([(ic,), head])

    # build run and post-process the MODFLOW 6 model
    name = "mymodel"
    sim = flopy.mf6.MFSimulation(
        sim_name=name,
        sim_ws=gridgen_ws,
        exe_name="mf6",
        verbosity_level=VERBOSITY_LEVEL,
    )
    tdis = flopy.mf6.ModflowTdis(sim)
    ims = flopy.mf6.ModflowIms(sim, linear_acceleration="bicgstab")
    gwf = flopy.mf6.ModflowGwf(sim, modelname=name, save_flows=True)
    disu = flopy.mf6.ModflowGwfdisu(gwf, **disu_gridprops)
    ic = flopy.mf6.ModflowGwfic(gwf)
    npf = flopy.mf6.ModflowGwfnpf(
        gwf, xt3doptions=True, save_specific_discharge=True
    )
    chd = flopy.mf6.ModflowGwfchd(gwf, stress_period_data=chdspd)
    budget_file = f"{name}.bud"
    head_file = f"{name}.hds"
    oc = flopy.mf6.ModflowGwfoc(
        gwf,
        budget_filerecord=budget_file,
        head_filerecord=head_file,
        saverecord=[("HEAD", "ALL"), ("BUDGET", "ALL")],
    )
    sim.write_simulation()

    gwf.modelgrid.set_coord_info(angrot=15)

    # The flopy Gridgen object includes the plottable layer number to the
    # diagonal position in the ihc array.  This is why and how modelgrid.nlay
    # is set to 3 and ncpl has a different number of cells per layer.
    assert gwf.modelgrid.nlay == 3
    assert np.allclose(gwf.modelgrid.ncpl, np.array([436, 184, 112]))

    # write grid and model shapefiles
    fname = os.path.join(gridgen_ws, "grid.shp")
    gwf.modelgrid.write_shapefile(fname)
    fname = os.path.join(gridgen_ws, "model.shp")
    gwf.export(fname)

    if mf6_exe is not None:
        sim.run_simulation(silent=True)
        head = gwf.output.head().get_data()
        bud = gwf.output.budget()
        spdis = bud.get_data(text="DATA-SPDIS")[0]

        if matplotlib is not None:
            f = plt.figure(figsize=(10, 10))
            vmin = head.min()
            vmax = head.max()
            for ilay in range(gwf.modelgrid.nlay):
                ax = plt.subplot(1, gwf.modelgrid.nlay, ilay + 1)
                pmv = flopy.plot.PlotMapView(gwf, layer=ilay, ax=ax)
                ax.set_aspect("equal")
                pmv.plot_array(
                    head.flatten(), cmap="jet", vmin=vmin, vmax=vmax
                )
                pmv.plot_grid(colors="k", alpha=0.1)
                pmv.contour_array(
                    head,
                    levels=[0.2, 0.4, 0.6, 0.8],
                    linewidths=3.0,
                    vmin=vmin,
                    vmax=vmax,
                )
                ax.set_title(f"Layer {ilay + 1}")
                pmv.plot_vector(spdis["qx"], spdis["qy"], color="white")
            fname = "results.png"
            fname = os.path.join(gridgen_ws, fname)
            plt.savefig(fname)
            plt.close("all")

            # check plot_bc works for unstructured mf6 grids
            # (for each layer, and then for all layers in one plot)
            plot_ranges = [range(gwf.modelgrid.nlay), range(1)]
            plot_alls = [False, True]
            for plot_range, plot_all in zip(plot_ranges, plot_alls):
                f_bc = plt.figure(figsize=(10, 10))
                for ilay in plot_range:
                    ax = plt.subplot(1, plot_range[-1] + 1, ilay + 1)
                    pmv = flopy.plot.PlotMapView(gwf, layer=ilay, ax=ax)
                    ax.set_aspect("equal")

                    pmv.plot_bc(
                        "CHD", plotAll=plot_all, edgecolor="None", zorder=2
                    )
                    pmv.plot_grid(
                        colors="k", linewidth=0.3, alpha=0.1, zorder=1
                    )

                    if len(ax.collections) == 0:
                        raise AssertionError(
                            "Boundary condition was not drawn"
                        )

                    for col in ax.collections:
                        if not isinstance(
                            col, (QuadMesh, PathCollection, LineCollection)
                        ):
                            raise AssertionError("Unexpected collection type")
                plt.close()

            # test plotting
            disu_dot_plot(gridgen_ws)

    return


def test_mfusg():
    # set up a gridgen workspace
    gridgen_ws = f"{baseDir}_mfusg"
    testFramework = flopyTest(verbose=True, testDirs=gridgen_ws, create=True)

    name = "dummy"
    nlay = 3
    nrow = 10
    ncol = 10
    delr = delc = 1.0
    top = 1
    bot = 0
    dz = (top - bot) / nlay
    botm = [top - k * dz for k in range(1, nlay + 1)]

    # create dummy model and dis package for gridgen
    m = flopy.modflow.Modflow(modelname=name, model_ws=gridgen_ws)
    dis = flopy.modflow.ModflowDis(
        m,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=top,
        botm=botm,
    )

    # Create and build the gridgen model with a refined area in the middle
    g = Gridgen(dis, model_ws=gridgen_ws)
    polys = [Polygon([(4, 4), (6, 4), (6, 6), (4, 6)])]
    g.add_refinement_features(polys, "polygon", 3, layers=[0])
    g.build()

    chdspd = []
    for x, y, head in [(0, 10, 1.0), (10, 0, 0.0)]:
        ra = g.intersect([(x, y)], "point", 0)
        ic = ra["nodenumber"][0]
        chdspd.append([ic, head, head])

    # gridprops = g.get_gridprops()
    gridprops = g.get_gridprops_disu5()

    # create the mfusg modoel
    name = "mymodel"
    m = flopy.mfusg.MfUsg(
        modelname=name,
        model_ws=gridgen_ws,
        exe_name=mfusg_exe,
        structured=False,
    )
    disu = flopy.mfusg.MfUsgDisU(m, **gridprops)
    bas = flopy.modflow.ModflowBas(m)
    lpf = flopy.mfusg.MfUsgLpf(m)
    chd = flopy.modflow.ModflowChd(m, stress_period_data=chdspd)
    sms = flopy.mfusg.MfUsgSms(m)
    oc = flopy.modflow.ModflowOc(m, stress_period_data={(0, 0): ["save head"]})
    m.write_input()

    # MODFLOW-USG does not have vertices, so we need to create
    # and unstructured grid and then assign it to the model. This
    # will allow plotting and other features to work properly.
    gridprops_ug = g.get_gridprops_unstructuredgrid()
    ugrid = flopy.discretization.UnstructuredGrid(**gridprops_ug, angrot=-15)
    m.modelgrid = ugrid

    if mfusg_exe is not None:
        m.run_model()

        # head is returned as a list of head arrays for each layer
        head_file = os.path.join(gridgen_ws, f"{name}.hds")
        head = flopy.utils.HeadUFile(head_file).get_data()

        if matplotlib is not None:
            f = plt.figure(figsize=(10, 10))
            vmin = 0.0
            vmax = 1.0
            for ilay in range(disu.nlay):
                ax = plt.subplot(1, g.nlay, ilay + 1)
                pmv = flopy.plot.PlotMapView(m, layer=ilay, ax=ax)
                ax.set_aspect("equal")
                pmv.plot_array(head[ilay], cmap="jet", vmin=vmin, vmax=vmax)
                pmv.plot_grid(colors="k", alpha=0.1)
                pmv.contour_array(
                    head[ilay], levels=[0.2, 0.4, 0.6, 0.8], linewidths=3.0
                )
                ax.set_title(f"Layer {ilay + 1}")
                # pmv.plot_specific_discharge(spdis, color='white')
            fname = "results.png"
            fname = os.path.join(gridgen_ws, fname)
            plt.savefig(fname)
            plt.close("all")

            # check plot_bc works for unstructured mfusg grids
            # (for each layer, and then for all layers in one plot)
            plot_ranges = [range(disu.nlay), range(1)]
            plot_alls = [False, True]
            for plot_range, plot_all in zip(plot_ranges, plot_alls):
                f_bc = plt.figure(figsize=(10, 10))
                for ilay in plot_range:
                    ax = plt.subplot(1, plot_range[-1] + 1, ilay + 1)
                    pmv = flopy.plot.PlotMapView(m, layer=ilay, ax=ax)
                    ax.set_aspect("equal")

                    pmv.plot_bc(
                        "CHD", plotAll=plot_all, edgecolor="None", zorder=2
                    )
                    pmv.plot_grid(
                        colors="k", linewidth=0.3, alpha=0.1, zorder=1
                    )

                    if len(ax.collections) == 0:
                        raise AssertionError(
                            "Boundary condition was not drawn"
                        )

                    for col in ax.collections:
                        if not isinstance(
                            col, (QuadMesh, PathCollection, LineCollection)
                        ):
                            raise AssertionError("Unexpected collection type")
                plt.close()

        # re-run with an LPF keyword specified. This would have thrown an error
        # before the addition of ikcflag to mflpf.py (flopy 3.3.3 and earlier).
        lpf = flopy.mfusg.MfUsgLpf(m, novfc=True, nocvcorrection=True)
        m.write_input()
        m.run_model()

        # also test load of unstructured LPF with keywords
        lpf2 = flopy.mfusg.MfUsgLpf.load(
            os.path.join(gridgen_ws, f"{name}.lpf"), m, check=False
        )
        msg = "NOCVCORRECTION and NOVFC should be in lpf options but at least one is not."
        assert (
            "NOVFC" in lpf2.options.upper()
            and "NOCVCORRECTION" in lpf2.options.upper()
        ), msg

    # test disu, bas6, lpf shapefile export for mfusg unstructured models
    try:
        m.disu.export(os.path.join(gridgen_ws, f"{name}_disu.shp"))
    except:
        raise AssertionError("Error exporting mfusg disu to shapefile.")
    try:
        m.bas6.export(os.path.join(gridgen_ws, f"{name}_bas6.shp"))
    except:
        raise AssertionError("Error exporting mfusg bas6 to shapefile.")
    try:
        m.lpf.export(os.path.join(gridgen_ws, f"{name}_lpf.shp"))
    except:
        raise AssertionError("Error exporting mfusg lpf to shapefile.")
    try:
        m.export(os.path.join(gridgen_ws, f"{name}.shp"))
    except:
        raise AssertionError("Error exporting mfusg model to shapefile.")

    return


def disv_dot_plot(sim_path):
    # load up the vertex example problem
    name = "mymodel"
    sim = flopy.mf6.MFSimulation.load(
        sim_name=name, version="mf6", exe_name="mf6", sim_ws=sim_path
    )
    # get gwf model
    gwf = sim.get_model(name)

    # get the dis package
    dis = gwf.disv

    # try plotting an array
    top = dis.top
    ax = top.plot()
    assert ax
    plt.close("all")

    # try plotting a package
    ax = dis.plot()
    assert ax
    plt.close("all")

    # try plotting a model
    ax = gwf.plot()
    assert ax
    plt.close("all")

    return


def disu_dot_plot(sim_path):
    # load up the disu example problem
    name = "mymodel"
    sim = flopy.mf6.MFSimulation.load(
        sim_name=name, version="mf6", exe_name="mf6", sim_ws=sim_path
    )
    gwf = sim.get_model(name)

    # check to make sure that ncpl was set properly through the diagonal
    # position of the ihc array
    assert np.allclose(gwf.modelgrid.ncpl, np.array([436, 184, 112]))

    # get the dis package
    dis = gwf.disu

    # try plotting an array
    top = dis.top
    ax = top.plot()
    assert ax
    plt.close("all")

    # try plotting a package
    ax = dis.plot()
    assert ax
    plt.close("all")

    # try plotting a model
    ax = gwf.plot()
    assert ax
    plt.close("all")

    return


if __name__ == "__main__":
    test_mf6disv()
    test_mf6disu()
    test_mfusg()
