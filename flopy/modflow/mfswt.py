"""
mfswt module.  Contains the ModflowSwt class. Note that the user can access
the ModflowSub class as `flopy.modflow.ModflowSwt`.

Additional information for this MODFLOW package can be found at the `Online
MODFLOW Guide
<http://water.usgs.gov/ogw/modflow/MODFLOW-2005-Guide/swt.htm>`_.

"""
import numpy as np

from ..pakbase import Package
from ..utils import Util2d, Util3d, read1d


class ModflowSwt(Package):
    """
    MODFLOW SUB-WT Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.modflow.mf.Modflow`) to which
        this package will be added.
    ipakcb : int
        A flag that is used to determine if cell-by-cell budget data should be
        saved. If ipakcb is non-zero cell-by-cell budget data will be saved.
        (default is 0).
    iswtoc : int
        iswtoc is a flag used to control output of information generated by the
        SUB Package. (default is 0).
    nystm : int
        nsystm is the number of systems of interbeds. (default is 1).
    ithk : int
        ithk is a flag to determine how thicknesses of compressible sediments
        vary in response to changes in saturated thickness. If ithk < 1,
        thickness of compressible sediments is constant. If ithk > 0, thickness
        of compressible sediments varies in response to changes in saturated
        thickness. (default is 1).
    ivoid : int
        ivoid is a flag to determine how void ratios of compressible sediments
        vary in response to changes in saturated thickness. If ivoid < 1, void
        ratio will be treated as a constant. If ivoid > 0, void ratio will be
        treated as a variable. (default is 0).
    nn : int
        nn is the number of nodes used to discretize the half space to
        approximate the head distributions in systems of delay interbeds.
        (default is 20).
    istpcs : int
        istpcs is a flag to determine how initial preconsolidation stress will
        be obtained. If istpcs does not equal 0, an array of offset values will
        be read in for each model layer. The offset values will be added to the
        initial effective stress to get initial preconsolidation stress. If
        istpcs = 0, an array with initial preconsolidation stress values will
        be read. (default is 1).
    icrcc : int
        icrcc is a flag to determine how recompression and compression indices
        will be obtained. If ICRCC is not equal to 0, arrays of elastic
        specific storage and inelastic skeletal specific storage will be read
        for each system of interbeds; the recompression index and compression
        index will not be read. If icrcc = 0, arrays of recompression index
        and compression index will be read for each system of interbeds;
        elastic skeletal specific storage and inelastic skeletal specific
        storage will not be read. (default is 0).
    lnwt : int or array of ints (nsystm)
        lnwt is a one-dimensional array specifying the model layer assignments
        for each system of interbeds. (default is 0).
    izcfl : int
        izcfl is a flag to specify whether or not initial calculated
        values of layer-center elevation will be printed. (default is 0).
    izcfm : int
        izcfm is is a code for the format in which layer-center elevation will
        be printed. (default is 0).
    iglfl : int
        iglfl is a flag to specify whether or not initial calculated values of
        geostatic stress will be printed. (default is 0).
    iglfm : int
        iglfm is a code for the format in which geostatic stress will be
        printed. (default is 0).
    iestfl : int
        iestfl is a flag to specify whether or not initial calculated values of
        effective stress will be printed. (default is 0).
    iestfm : int
        iestfm is a code for the format in which effective stress will be
        printed. (default is 0).
    ipcsfl : int
        ipcsfl is a flag to specify whether or not initial calculated values of
        preconsolidation stress will be printed. (default is 0).
    ipcsfm : int
        ipcsfm is a code for the format in which preconsolidation stress will
        be printed. (default is 0).
    istfl : int
        istfl is a flag to specify whether or not initial equivalent storage
        properties will be printed for each system of interbeds. If icrcc is
        not equal to 0, the
        equivalent storage properties that can be printed are recompression and
        compression indices (cr and cc), which are calculated from elastic and
        inelastic skeletal specific storage (sske and sskv). If icrcc = 0,
        equivalent storage properties that can be printed are elastic and
        inelastic skeletal specific storage, which are calculated from the
        recompression and compression indices. (default is 0).
    istfm : int
        istfm is a code for the format in which equivalent storage properties
        will be printed. (default is 0).
    gl0 : float or array of floats (nrow, ncol)
        gl0 is an array specifying the geostatic stress above model layer 1. If
        the top of model layer 1 is the land surface, enter values of zero for
        this array. (default is 0.).
    sgm : float or array of floats (nrow, ncol)
        sgm is an array specifying the specific gravity of moist or unsaturated
        sediments. (default is 1.7).
    sgs : float or array of floats (nrow, ncol)
        sgs is an array specifying the specific gravity of saturated sediments.
        (default is 2.).
    thick : float or array of floats (nsystm, nrow, ncol)
        thick is an array specifying the thickness of compressible sediments.
        (default is 1.).
    sse : float or array of floats (nsystm, nrow, ncol)
        sse is an array specifying the initial elastic skeletal specific
        storage of compressible beds. sse is not used if icrcc = 0.
        (default is 1.).
    ssv : float or array of floats (nsystm, nrow, ncol)
        ssv is an array specifying the initial inelastic skeletal specific
        storage of compressible beds. ssv is not used if icrcc = 0.
        (default is 1.).
    cr : float or array of floats (nsystm, nrow, ncol)
        cr is an array specifying the recompression index of compressible beds.
        cr is not used if icrcc is not equal to 0. (default is 0.01).
    cc : float or array of floats (nsystm, nrow, ncol)
        cc is an array specifying the compression index of compressible beds
        cc is not used if icrcc is not equal to 0. (default is 0.25).
    void : float or array of floats (nsystm, nrow, ncol)
        void is an array specifying the initial void ratio of compressible
        beds. (default is 0.82).
    sub : float or array of floats (nsystm, nrow, ncol)
        sub is an array specifying the initial compaction in each system of
        interbeds. Compaction values computed by the package are added to
        values in this array so that printed or stored values of compaction and
        land subsidence may include previous components. Values in this array
        do not affect calculations of storage changes or resulting compaction.
        For simulations in which output values will reflect compaction and
        subsidence since the start of the simulation, enter zero values for all
        elements of this array. (default is 0.).
    pcsoff : float or array of floats (nlay, nrow, ncol)
        pcsoff is an array specifying the offset from initial effective stress
        to initial preconsolidation stress at the bottom of the model layer in
        units of height of a column of water. pcsoff is not used if istpcs=0.
        (default is 0.).
    pcs : float or array of floats (nlay, nrow, ncol)
        pcs is an array specifying the initial preconsolidation stress, in
        units of height of a column of water, at the bottom of the model layer.
        pcs is not used if istpcs is not equal to 0. (default is 0.).
    ids16 : list or array of ints (26)
        Format codes and unit numbers for swtsidence, compaction by model
        layer, compaction by interbed system, vertical displacement,
        preconsolidation stress, change in preconsolidation stress, geostatic
        stress, change in geostatic stress, effective stress, void ration,
        thickness of compressible sediments, and layer-center elevation will be
        printed. If ids16 is None and iswtoc>0 then print code 0 will be used
        for all data which is output to the binary swtsidence output file
        (unit=1054). The 26 entries in ids16 correspond to ifm1, iun1, ifm2,
        iun2, ifm3, iun3, ifm4, iun4, ifm5, iun5, ifm6, iun6, ifm7, iun7, ifm8,
        iun8, ifm9, iun9, ifm10, iun11, ifm12, iun12, ifm13, and iun13
        variables. (default is None).
    ids17 : list or array of ints (iswtoc, 30)
        Stress period and time step range and print and save flags used to
        control printing and saving of information generated by the SUB-WT
        Package during program execution. Each row of ids17 corresponds to
        isp1, isp2, its1, its2, ifl1, ifl2, ifl3, ifl4, ifl5, ifl6, ifl7,
        ifl8, ifl9, ifl10, ifl11, ifl12, ifl13, ifl14, ifl15, ifl16, ifl17,
        ifl18, ifl9, ifl20, ifl21, ifl22, ifl23, ifl24, ifl25, and ifl26
        variables for iswtoc entries. isp1, isp2, its1, and its2 are stress
        period and time step ranges. ifl1 and ifl2 control subsidence printing
        and saving. ifl3 and ifl4 control compaction by model layer printing
        and saving. ifl5 and ifl6 control compaction by interbed system
        printing and saving. ifl7 and ifl8 control vertical displacement
        printing and saving. ifl9 and ifl10 control preconsolidation stress
        printing and saving. ifl11 and ifl12 control change in preconsolidation
        stress printing and saving. ifl13 and ifl14 control geostatic stress
        printing and saving. ifl15 and ifl16 control change in geostatic stress
        printing and saving. ifl17 and ifl18 control effective stress printing
        and saving. ifl19 and ifl20 control change in effective stress printing
        and saving. ifl21 and ifl22 control void ratio printing and saving.
        ifl23 and ifl24 control compressible bed thickness printing and saving.
        ifl25 and ifl26 control layer-center elevation printing and saving.
        If ids17 is None and iswtoc>0 then all available subsidence output will
        be printed and saved to the binary subsidence output file (unit=1054).
        (default is None).
    unitnumber : int
        File unit number (default is None).
    filenames : str or list of str
        Filenames to use for the package and the output files. If
        filenames=None the package name will be created using the model name
        and package extension and the cbc output name and other swt output
        files will be created using the model name and .cbc and swt output
        extensions (for example, modflowtest.cbc), if ipakcbc and other
        swt output files (dataset 16) are numbers greater than zero.
        If a single string is passed the package name will be set to the
        string and other swt output files will be set to the model name with
        the appropriate output file extensions. To define the names for all
        package files (input and output) the length of the list of strings
        should be 15.
        Default is None.

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----
    Parameters are supported in Flopy only when reading in existing models.
    Parameter values are converted to native values in Flopy and the
    connection to "parameters" is thus nonexistent. Parameters are not
    supported in the SUB-WT Package.

    Examples
    --------

    >>> import flopy
    >>> m = flopy.modflow.Modflow()
    >>> swt = flopy.modflow.ModflowSwt(m)

    """

    def write_file(self, f=None):
        """
        Write the package file.

        Returns
        -------
        None

        """
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        if f is None:
            f = open(self.fn_path, "w")
        # First line: heading
        f.write(f"{self.heading}\n")
        # write dataset 1
        f.write(
            "{} {} {} {} {} {} {}\n".format(
                self.ipakcb,
                self.iswtoc,
                self.nsystm,
                self.ithk,
                self.ivoid,
                self.istpcs,
                self.icrcc,
            )
        )
        # write dataset 2
        t = self.lnwt.array
        for tt in t:
            f.write(f"{tt + 1} ")
        f.write("\n")

        # write dataset 3
        f.write(
            "{} {} {} {} {} {} {} {} {} {}\n".format(
                self.izcfl,
                self.izcfm,
                self.iglfl,
                self.iglfm,
                self.iestfl,
                self.iestfm,
                self.ipcsfl,
                self.ipcsfm,
                self.istfl,
                self.istfm,
            )
        )

        # write dataset 4
        f.write(self.gl0.get_file_entry())

        # write dataset 5
        f.write(self.sgm.get_file_entry())

        # write dataset 6
        f.write(self.sgs.get_file_entry())

        # write datasets 7 to 13
        for k in range(self.nsystm):
            f.write(self.thick[k].get_file_entry())
            if self.icrcc != 0:
                f.write(self.sse[k].get_file_entry())
                f.write(self.ssv[k].get_file_entry())
            else:
                f.write(self.cr[k].get_file_entry())
                f.write(self.cc[k].get_file_entry())
            f.write(self.void[k].get_file_entry())
            f.write(self.sub[k].get_file_entry())

        # write datasets 14 and 15
        for k in range(nlay):
            if self.istpcs != 0:
                f.write(self.pcsoff[k].get_file_entry())
            else:
                f.write(self.pcs[k].get_file_entry())

        # write dataset 16 and 17
        if self.iswtoc > 0:
            # dataset 16
            for i in self.ids16:
                f.write(f"{i} ")
            f.write("  #dataset 16\n")

            # dataset 17
            for k in range(self.iswtoc):
                t = self.ids17[k, :].copy()
                t[0:4] += 1
                for i in t:
                    f.write(f"{i} ")
                f.write(f"  #dataset 17 iswtoc {k + 1}\n")

        # close swt file
        f.close()

    def __init__(
        self,
        model,
        ipakcb=None,
        iswtoc=0,
        nsystm=1,
        ithk=0,
        ivoid=0,
        istpcs=1,
        icrcc=0,
        lnwt=0,
        izcfl=0,
        izcfm=0,
        iglfl=0,
        iglfm=0,
        iestfl=0,
        iestfm=0,
        ipcsfl=0,
        ipcsfm=0,
        istfl=0,
        istfm=0,
        gl0=0.0,
        sgm=1.7,
        sgs=2.0,
        thick=1.0,
        sse=1.0,
        ssv=1.0,
        cr=0.01,
        cc=0.25,
        void=0.82,
        sub=0.0,
        pcsoff=0.0,
        pcs=0.0,
        ids16=None,
        ids17=None,
        extension="swt",
        unitnumber=None,
        filenames=None,
    ):
        """
        Package constructor.

        """
        # set default unit number of one is not specified
        if unitnumber is None:
            unitnumber = ModflowSwt._defaultunit()

        # set filenames
        if filenames is None:
            filenames = [None for x in range(15)]
        elif isinstance(filenames, str):
            filenames = [filenames] + [None for x in range(14)]
        elif isinstance(filenames, list):
            if len(filenames) < 15:
                n = 15 - len(filenames) + 1
                filenames = filenames + [None for x in range(n)]

        # update external file information with cbc output, if necessary
        if ipakcb is not None:
            fname = filenames[1]
            model.add_output_file(
                ipakcb, fname=fname, package=ModflowSwt._ftype()
            )
        else:
            ipakcb = 0

        item16_extensions = [
            "swt_subsidence.hds",
            "swt_total_comp.hds",
            "swt_inter_comp.hds",
            "swt_vert_disp.hds",
            "swt_precon_stress.hds",
            "swt_precon_stress_delta.hds",
            "swt_geostatic_stress.hds",
            "swt_geostatic_stress_delta.hds",
            "swt_eff_stress.hds",
            "swt_eff_stress_delta.hds",
            "swt_void_ratio.hds",
            "swt_thick.hds",
            "swt_lay_center.hds",
        ]
        item16_units = [2052 + i for i in range(len(item16_extensions))]

        if iswtoc > 0:
            idx = 0
            for k in range(1, 26, 2):
                ext = item16_extensions[idx]
                if ids16 is None:
                    iu = item16_units[idx]
                else:
                    iu = ids16[k]
                fname = filenames[idx + 2]
                model.add_output_file(
                    iu, fname=fname, extension=ext, package=ModflowSwt._ftype()
                )
                idx += 1

        extensions = [extension]
        name = [ModflowSwt._ftype()]
        units = [unitnumber]
        extra = [""]

        # set package name
        fname = [filenames[0]]

        # Call ancestor's init to set self.parent, extension, name and
        # unit number
        Package.__init__(
            self,
            model,
            extension=extensions,
            name=name,
            unit_number=units,
            extra=extra,
            filenames=fname,
        )

        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper

        self._generate_heading()
        self.url = "swt.htm"

        self.ipakcb = ipakcb
        self.iswtoc = iswtoc

        self.nsystm = nsystm
        self.ithk = ithk
        self.ivoid = ivoid
        self.istpcs = istpcs
        self.icrcc = icrcc

        self.lnwt = Util2d(model, (nsystm,), np.int32, lnwt, name="lnwt")

        self.izcfl = izcfl
        self.izcfm = izcfm
        self.iglfl = iglfl
        self.iglfm = iglfm
        self.iestfl = iestfl
        self.iestfm = iestfm
        self.ipcsfl = ipcsfl
        self.ipcsfm = ipcsfm
        self.istfl = istfl
        self.istfm = istfm

        self.gl0 = Util2d(model, (nrow, ncol), np.float32, gl0, name="gl0")
        self.sgm = Util2d(model, (nrow, ncol), np.float32, sgm, name="sgm")
        self.sgs = Util2d(model, (nrow, ncol), np.float32, sgs, name="sgs")

        # interbed data
        names = ["thick system " for n in range(nsystm)]
        self.thick = Util3d(
            model,
            (nsystm, nrow, ncol),
            np.float32,
            thick,
            name=names,
            locat=self.unit_number[0],
        )
        names = ["void system " for n in range(nsystm)]
        self.void = Util3d(
            model,
            (nsystm, nrow, ncol),
            np.float32,
            void,
            name=names,
            locat=self.unit_number[0],
        )
        names = ["sub system " for n in range(nsystm)]
        self.sub = Util3d(
            model,
            (nsystm, nrow, ncol),
            np.float32,
            sub,
            name=names,
            locat=self.unit_number[0],
        )
        if icrcc != 0:
            names = ["sse system " for n in range(nsystm)]
            self.sse = Util3d(
                model,
                (nsystm, nrow, ncol),
                np.float32,
                sse,
                name=names,
                locat=self.unit_number[0],
            )
            names = ["ssc system " for n in range(nsystm)]
            self.ssv = Util3d(
                model,
                (nsystm, nrow, ncol),
                np.float32,
                ssv,
                name=names,
                locat=self.unit_number[0],
            )
            self.cr = None
            self.cc = None
        else:
            self.sse = None
            self.ssv = None
            names = ["cr system " for n in range(nsystm)]
            self.cr = Util3d(
                model,
                (nsystm, nrow, ncol),
                np.float32,
                cr,
                name=names,
                locat=self.unit_number[0],
            )
            names = ["cc system " for n in range(nsystm)]
            self.cc = Util3d(
                model,
                (nsystm, nrow, ncol),
                np.float32,
                cc,
                name=names,
                locat=self.unit_number[0],
            )

        # layer data
        if istpcs != 0:
            self.pcsoff = Util3d(
                model,
                (nlay, nrow, ncol),
                np.float32,
                pcsoff,
                name="pcsoff",
                locat=self.unit_number[0],
            )
            self.pcs = None
        else:
            self.pcsoff = None
            self.pcs = Util3d(
                model,
                (nlay, nrow, ncol),
                np.float32,
                pcs,
                name="pcs",
                locat=self.unit_number[0],
            )

        # output data
        if iswtoc > 0:
            if ids16 is None:
                self.ids16 = np.zeros((26), dtype=np.int32)
                ui = 0
                for i in range(1, 26, 2):
                    self.ids16[i] = item16_units[ui]
                    ui += 1
            else:
                if isinstance(ids16, list):
                    ds16 = np.array(ids16)
                assert len(ids16) == 26
                self.ids16 = ids16

            if ids17 is None:
                ids17 = np.ones((30), dtype=np.int32)
                ids17[0] = 0
                ids17[2] = 0
                ids17[1] = 9999
                ids17[3] = 9999
                self.ids17 = np.atleast_2d(ids17)
            else:
                if isinstance(ids17, list):
                    ids17 = np.atleast_2d(np.array(ids17))
                assert ids17.shape[1] == 30
                self.ids17 = ids17

        # add package to model
        self.parent.add_package(self)

    @classmethod
    def load(cls, f, model, ext_unit_dict=None):
        """
        Load an existing package.

        Parameters
        ----------
        f : filename or file handle
            File to load.
        model : model object
            The model object (of type :class:`flopy.modflow.mf.Modflow`) to
            which this package will be added.
        ext_unit_dict : dictionary, optional
            If the arrays in the file are specified using EXTERNAL,
            or older style array control records, then `f` should be a file
            handle.  In this case ext_unit_dict is required, which can be
            constructed using the function
            :class:`flopy.utils.mfreadnam.parsenamefile`.

        Returns
        -------
        swt : ModflowSwt object

        Examples
        --------

        >>> import flopy
        >>> m = flopy.modflow.Modflow()
        >>> swt = flopy.modflow.ModflowSwt.load('test.swt', m)

        """

        if model.verbose:
            print("loading swt package file...")

        openfile = not hasattr(f, "read")
        if openfile:
            filename = f
            f = open(filename, "r")

        # dataset 0 -- header
        while True:
            line = f.readline()
            if line[0] != "#":
                break
        # determine problem dimensions
        nrow, ncol, nlay, nper = model.get_nrow_ncol_nlay_nper()

        # read dataset 1
        if model.verbose:
            print("  loading swt dataset 1")
        t = line.strip().split()
        ipakcb, iswtoc, nsystm, ithk, ivoid, istpcs, icrcc = (
            int(t[0]),
            int(t[1]),
            int(t[2]),
            int(t[3]),
            int(t[4]),
            int(t[5]),
            int(t[6]),
        )

        # if ipakcb > 0:
        #     ipakcb = 53

        # read dataset 2
        lnwt = None
        if nsystm > 0:
            if model.verbose:
                print("  loading swt dataset 2")
            lnwt = np.empty((nsystm), dtype=np.int32)
            lnwt = read1d(f, lnwt) - 1

        # read dataset 3
        if model.verbose:
            print("  loading swt dataset 3")
        line = f.readline()
        t = line.strip().split()
        (
            iizcfl,
            izcfm,
            iglfl,
            iglfm,
            iestfl,
            iestfm,
            ipcsfl,
            ipcsfm,
            istfl,
            istfm,
        ) = (
            int(t[0]),
            int(t[1]),
            int(t[2]),
            int(t[3]),
            int(t[4]),
            int(t[5]),
            int(t[6]),
            int(t[7]),
            int(t[8]),
            int(t[9]),
        )

        # read dataset 4
        if model.verbose:
            print("  loading swt dataset 4")
        gl0 = Util2d.load(
            f, model, (nrow, ncol), np.float32, "gl0", ext_unit_dict
        )

        # read dataset 5
        if model.verbose:
            print("  loading swt dataset 5")
        sgm = Util2d.load(
            f, model, (nrow, ncol), np.float32, "sgm", ext_unit_dict
        )

        # read dataset 6
        if model.verbose:
            print("  loading swt dataset 6")
        sgs = Util2d.load(
            f, model, (nrow, ncol), np.float32, "sgs", ext_unit_dict
        )

        # read datasets 7 to 13
        thick = [0] * nsystm
        void = [0] * nsystm
        sub = [0] * nsystm
        if icrcc == 0:
            sse = None
            ssv = None
            cr = [0] * nsystm
            cc = [0] * nsystm
        else:
            sse = [0] * nsystm
            ssv = [0] * nsystm
            cr = None
            cc = None

        for k in range(nsystm):
            kk = lnwt[k] + 1
            # thick
            if model.verbose:
                print(f"  loading swt dataset 7 for layer {kk}")
            t = Util2d.load(
                f,
                model,
                (nrow, ncol),
                np.float32,
                f"thick layer {kk}",
                ext_unit_dict,
            )
            thick[k] = t
            if icrcc != 0:
                # sse
                if model.verbose:
                    print(f"  loading swt dataset 8 for layer {kk}")
                t = Util2d.load(
                    f,
                    model,
                    (nrow, ncol),
                    np.float32,
                    f"sse layer {kk}",
                    ext_unit_dict,
                )
                sse[k] = t
                # ssv
                if model.verbose:
                    print(f"  loading swt dataset 9 for layer {kk}")
                t = Util2d.load(
                    f,
                    model,
                    (nrow, ncol),
                    np.float32,
                    f"sse layer {kk}",
                    ext_unit_dict,
                )
                ssv[k] = t
            else:
                # cr
                if model.verbose:
                    print(f"  loading swt dataset 10 for layer {kk}")
                t = Util2d.load(
                    f,
                    model,
                    (nrow, ncol),
                    np.float32,
                    f"cr layer {kk}",
                    ext_unit_dict,
                )
                cr[k] = t
                # cc
                if model.verbose:
                    print(f"  loading swt dataset 11 for layer {kk}")
                t = Util2d.load(
                    f,
                    model,
                    (nrow, ncol),
                    np.float32,
                    f"cc layer {kk}",
                    ext_unit_dict,
                )
                cc[k] = t
            # void
            if model.verbose:
                print(f"  loading swt dataset 12 for layer {kk}")
            t = Util2d.load(
                f,
                model,
                (nrow, ncol),
                np.float32,
                f"void layer {kk}",
                ext_unit_dict,
            )
            void[k] = t
            # sub
            if model.verbose:
                print(f"  loading swt dataset 13 for layer {kk}")
            t = Util2d.load(
                f,
                model,
                (nrow, ncol),
                np.float32,
                f"sub layer {kk}",
                ext_unit_dict,
            )
            sub[k] = t

        # dataset 14 and 15
        if istpcs != 0:
            pcsoff = [0] * nlay
            pcs = None
        else:
            pcsoff = None
            pcs = [0] * nlay
        for k in range(nlay):
            if istpcs != 0:
                if model.verbose:
                    print(f"  loading swt dataset 14 for layer {kk}")
                t = Util2d.load(
                    f,
                    model,
                    (nrow, ncol),
                    np.float32,
                    f"pcsoff layer {k + 1}",
                    ext_unit_dict,
                )
                pcsoff[k] = t
            else:
                if model.verbose:
                    print(f"  loading swt dataset 15 for layer {kk}")
                t = Util2d.load(
                    f,
                    model,
                    (nrow, ncol),
                    np.float32,
                    f"pcs layer {k + 1}",
                    ext_unit_dict,
                )
                pcs[k] = t

        ids16 = None
        ids17 = None
        if iswtoc > 0:
            # dataset 16
            if model.verbose:
                print(f"  loading swt dataset 15 for layer {kk}")
            ids16 = np.empty(26, dtype=np.int32)
            ids16 = read1d(f, ids16)
            # for k in range(1, 26, 2):
            #    model.add_pop_key_list(ids16[k])
            #    ids16[k] = 2054  # all sub-wt data sent to unit 2054
            # dataset 17
            ids17 = [0] * iswtoc
            for k in range(iswtoc):
                if model.verbose:
                    print(f"  loading swt dataset 17 for iswtoc {k + 1}")
                t = np.empty(30, dtype=np.int32)
                t = read1d(f, t)
                t[0:4] -= 1
                ids17[k] = t

        if openfile:
            f.close()

        # determine specified unit number
        unitnumber = None
        filenames = [None for x in range(15)]
        if ext_unit_dict is not None:
            unitnumber, filenames[0] = model.get_ext_dict_attr(
                ext_unit_dict, filetype=ModflowSwt._ftype()
            )
            if ipakcb > 0:
                iu, filenames[1] = model.get_ext_dict_attr(
                    ext_unit_dict, unit=ipakcb
                )

            if iswtoc > 0:
                ipos = 2
                for k in range(1, 26, 2):
                    unit = ids16[k]
                    if unit > 0:
                        iu, filenames[ipos] = model.get_ext_dict_attr(
                            ext_unit_dict, unit=unit
                        )
                        model.add_pop_key_list(unit)
                    ipos += 1

        # return sut-wt instance
        return cls(
            model,
            ipakcb=ipakcb,
            iswtoc=iswtoc,
            nsystm=nsystm,
            ithk=ithk,
            ivoid=ivoid,
            istpcs=istpcs,
            icrcc=icrcc,
            lnwt=lnwt,
            izcfl=iizcfl,
            izcfm=izcfm,
            iglfl=iglfl,
            iglfm=iglfm,
            iestfl=iestfl,
            iestfm=iestfm,
            ipcsfl=ipcsfl,
            ipcsfm=ipcsfm,
            istfl=istfl,
            istfm=istfm,
            gl0=gl0,
            sgm=sgm,
            sgs=sgs,
            thick=thick,
            sse=sse,
            ssv=ssv,
            cr=cr,
            cc=cc,
            void=void,
            sub=sub,
            pcsoff=pcsoff,
            pcs=pcs,
            ids16=ids16,
            ids17=ids17,
            unitnumber=unitnumber,
            filenames=filenames,
        )

    @staticmethod
    def _ftype():
        return "SWT"

    @staticmethod
    def _defaultunit():
        return 35
