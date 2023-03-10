"""
mtbtn module. Contains the Mt3dBtn class. Note that the user can access
the Mt3dBtn class as `flopy.mt3d.Mt3dBtn`.

Additional information for this MT3DMS package can be found in the MT3DMS
User's Manual.

"""

import numpy as np
# from numpy import empty,array
from ..pakbase import Package
from ..utils import Util2d, Util3d, read1d
import warnings

class Mt3dBtn(Package):
    """
    Basic Transport Package Class.

    Parameters
    ----------
    model : model object
        The model object (of type :class:`flopy.mt3dms.mt.Mt3dms`) to which
        this package will be added.
    ncomp : int
        The total number of chemical species in the simulation. (default is
        None, will be changed to 1 if sconc is single value)
    mcomp : int
        The total number of 'mobile' species (default is 1). mcomp must be
        equal or less than ncomp.
    tunit : str
        The name of unit for time (default is 'D', for 'days'). Used for
        identification purposes only.
    lunit : str
        The name of unit for length (default is 'M', for 'meters'). Used for
        identification purposes only.
    munit : str
        The name of unit for mass (default is 'KG', for 'kilograms'). Used for
        identification purposes only.
    prsity : float or array of floats (nlay, nrow, ncol)
        The effective porosity of the porous medium in a single porosity
        system, or the mobile porosity in a dual-porosity medium (the immobile
        porosity is defined through the Chemical Reaction Package. (default is
        0.25).
    icbund : int or array of ints (nlay, nrow, ncol)
        The icbund array specifies the boundary condition type for solute
        species (shared by all species). If icbund = 0, the cell is an inactive
        concentration cell; If icbund < 0, the cell is a constant-concentration
        cell; If icbund > 0, the cell is an active concentration cell where the
        concentration value will be calculated. (default is 1).
    sconc : float, array of (nlay, nrow, ncol), or filename, or a list (length
        ncomp) of these for multi-species simulations
        The starting concentration for the solute transport simulation.
    cinact : float
        The value for indicating an inactive concentration cell. (default is
        1e30).
    thkmin : float
        The minimum saturated thickness in a cell, expressed as the decimal
        fraction of its thickness, below which the cell is considered inactive.
        (default is 0.01).
    ifmtcn : int
        A flag/format code indicating how the calculated concentration should
        be printed to the standard output text file. Format codes for printing
        are listed in Table 3 of the MT3DMS manual. If ifmtcn > 0 printing is
        in wrap form; ifmtcn < 0 printing is in strip form; if ifmtcn = 0
        concentrations are not printed. (default is 0).
    ifmtnp : int
        A flag/format code indicating how the number of particles should
        be printed to the standard output text file. The convention is
        the same as for ifmtcn. (default is 0).
    ifmtrf : int
        A flag/format code indicating how the calculated retardation factor
        should be printed to the standard output text file. The convention is
        the same as for ifmtcn. (default is 0).
    ifmtdp : int
        A flag/format code indicating how the distance-weighted dispersion
        coefficient should be printed to the standard output text file. The
        convention is the same as for ifmtcn. (default is 0).
    savucn : bool
        A logical flag indicating whether the concentration solution should be
        saved in an unformatted file. (default is True).
    nprs : int
        A flag indicating (i) the frequency of the output and
        (ii) whether the output frequency is specified in terms
        of total elapsed simulation time or the transport step number. If
        nprs > 0 results will be saved at the times as specified in timprs;
        if nprs = 0, results will not be saved except at the end of simulation;
        if NPRS < 0, simulation results will be saved whenever the number of
        transport steps is an even multiple of nprs. (default is 0).
    timprs : list of floats
        The total elapsed time at which the simulation results are saved. The
        number of entries in timprs must equal nprs. (default is None).
    obs: array of int
        An array with the cell indices (layer, row, column) for which the
        concentration is to be printed at every transport step. (default is
        None).
    nprobs: int
        An integer indicating how frequently the concentration at the specified
        observation points should be saved. (default is 1).
    chkmas: bool
        A logical flag indicating whether a one-line summary of mass balance
        information should be printed. (default is True).
    nprmas: int
        An integer indicating how frequently the mass budget information
        should be saved. (default is 1).
    dt0: float
        The user-specified initial transport step size within each time-step 
        of the flow solution. (default is 0).
    mxstrn: int
        The maximum number of transport steps allowed within one time step
        of the flow solution. (default is 50000).
    ttsmult: float
        The multiplier for successive transport steps within a flow time-step
        if the GCG solver is used and the solution option for the advection
        term is the standard finite-difference method. (default is 1.0).
    ttsmax: float
        The maximum transport step size allowed when transport step size
        multiplier TTSMULT > 1.0. (default is 0).
    species_names: list of str
        A list of names for every species in the simulation.
    extension : string
        Filename extension (default is 'btn')

    Attributes
    ----------

    Methods
    -------

    See Also
    --------

    Notes
    -----

    Examples
    --------

    >>> import flopy
    >>> mt = flopy.mt3dms.Mt3dms()
    >>> btn = flopy.mt3dms.Mt3dBtn(mt)

    """
    unitnumber = 31
    def __init__(self, model, nlay=None, nrow=None, ncol=None, nper=None,
                 ncomp=1, mcomp=1, tunit='D', lunit='M', munit='KG',
                 laycon=None, delr=None, delc=None, htop=None, dz=None,
                 prsity=0.30, icbund=1,
                 sconc=0.0, cinact=1e30, thkmin=0.01, ifmtcn=0, ifmtnp=0,
                 ifmtrf=0, ifmtdp=0, savucn=True, nprs=0, timprs=None,
                 obs=None, nprobs=1, chkmas=True, nprmas=1,
                 perlen=None, nstp=None, tsmult=None, ssflag=None, dt0=0,
                 mxstrn=50000, ttsmult=1.0, ttsmax=0,
                 species_names=None, extension='btn', **kwargs):
        Package.__init__(self, model, extension, 'BTN', self.unitnumber)

        # Set these variables from the Modflow model (self.parent.mf) unless
        # they are specified in the constructor.
        self.setmodflowvars(nlay, nrow, ncol, nper, laycon, delr, delc, htop,
                            dz, perlen, nstp, tsmult)

        # Make the rest of the assignments
        self.heading1 = '# BTN for MT3DMS, generated by Flopy.'
        self.heading2 = '#'
        self.ncomp = ncomp
        self.mcomp = mcomp
        self.tunit = tunit
        self.lunit = lunit
        self.munit = munit
        self.cinact = cinact
        self.thkmin = thkmin
        self.ifmtcn = ifmtcn
        self.ifmtnp = ifmtnp
        self.ifmtrf = ifmtrf
        self.ifmtdp = ifmtdp
        self.savucn = savucn
        self.nprs = nprs
        self.timprs = timprs
        self.obs = obs
        self.nprobs = nprobs
        self.chkmas = chkmas
        self.nprmas = nprmas
        if species_names is None:
            species_names = []
        self.species_names = species_names
        self.prsity = Util3d(model, (self.nlay, self.nrow, self.ncol),
                              np.float32, prsity, name='prsity',
                              locat=self.unit_number[0])
        self.icbund = Util3d(model, (self.nlay, self.nrow, self.ncol), np.int,
                              icbund, name='icbund',
                              locat=self.unit_number[0])
        self.ssflag = ssflag
        self.dt0 = Util2d(model, (self.nper,), np.float32, dt0, name='dt0')
        self.mxstrn = Util2d(model, (self.nper,), np.int, mxstrn,
                              name='mxstrn')
        self.ttsmult = Util2d(model, (self.nper,), np.float32, ttsmult,
                               name='ttmult')
        self.ttsmax = Util2d(model, (self.nper,), np.float32, ttsmax,
                              name='ttsmax')

        # Do some fancy stuff for multi-species concentrations
        self.sconc = []
        u3d = Util3d(model, (self.nlay, self.nrow, self.ncol), np.float32,
                      sconc, name='sconc1', locat=self.unit_number[0])
        self.sconc.append(u3d)
        if ncomp > 1:
            for icomp in range(2, ncomp + 1):
                name = "sconc" + str(icomp)
                val = 0.0
                if name in kwargs:
                    val = kwargs.pop(name)
                else:
                    print("BTN: setting sconc for component " +
                          str(icomp) + " to zero, kwarg name " +
                          name)
                u3d = Util3d(model, (self.nlay, self.nrow, self.ncol),
                              np.float32, val, name=name,
                              locat=self.unit_number[0])
                self.sconc.append(u3d)

        # Check to make sure that all kwargs have been consumed
        if len(list(kwargs.keys())) > 0:
            raise Exception("BTN error: unrecognized kwargs: " +
                            ' '.join(list(kwargs.keys())))

        # Finally add self to parent's package list and return
        self.parent.add_package(self)
        return

    def setmodflowvars(self, nlay, nrow, ncol, nper, laycon, delr, delc, htop,
                            dz, perlen, nstp, tsmult):
        '''
        Set these variables from the MODFLOW model, if it exists
        '''
        # Members that may come from a modflow model (model.mf)
        validmfdis = True
        try:
            dum = self.parent.mf.dis.nlay
        except:
            validmfdis = False

        mfvarlist = [nlay, nrow, ncol, nper, laycon, delr, delc, htop, dz,
                     perlen, nstp, tsmult]
        if not validmfdis:
            for v in mfvarlist:
                s = 'BTN error. Required input is None, but no modflow model.'
                s += ' If no modflow model is passed to Mt3dms, then values '
                s += 'must be specified in the BTN constructor for: '
                s += 'nlay, nrow, ncol, nper, laycon, delr, delc, htop, dz, '
                s += 'perlen, nstp, and tsmult.'
                if v is None:
                    raise Exception(s)

        if nlay is not None:
            self.nlay = nlay
        else:
            self.nlay = self.parent.mf.dis.nlay

        if nrow is not None:
            self.nrow = nrow
        else:
            self.nrow = self.parent.mf.dis.nrow

        if ncol is not None:
            self.ncol = ncol
        else:
            self.ncol = self.parent.mf.dis.ncol

        if nper is not None:
            self.nper = nper
        else:
            self.nper = self.parent.mf.dis.nper

        nlay = self.nlay
        nrow = self.nrow
        ncol = self.ncol
        nper = self.nper

        if delr is not None:
            self.delr = Util2d(self.parent, (ncol,), np.float32, delr,
                                name='delr',
                                locat=self.unit_number[0])
        else:
            self.delr = Util2d(self.parent, (ncol,), np.float32,
                                self.parent.mf.dis.delr.get_value(),
                                name='delr',
                                locat=self.unit_number[0])

        if delc is not None:
            self.delc = Util2d(self.parent, (nrow,), np.float32, delc,
                                name='delc',
                                locat=self.unit_number[0])
        else:
            self.delc = Util2d(self.parent, (nrow,), np.float32,
                                self.parent.mf.dis.delc.get_value(),
                                name='delc',
                                locat=self.unit_number[0])

        if htop is not None:
            self.htop = Util2d(self.parent, (nrow, ncol), np.float32, htop,
                                name='htop',
                                locat=self.unit_number[0])
        else:
            self.htop = Util2d(self.parent, (nrow, ncol), np.float32,
                                self.parent.mf.dis.top.get_value(),
                                name='htop',
                                locat=self.unit_number[0])

        if dz is not None:
            self.dz = Util3d(self.parent, (nlay, nrow, ncol), np.float32, dz,
                              name='dz',
                              locat=self.unit_number[0])
        else:
            thickness = self.parent.mf.dis.thickness.get_value()
            self.dz = Util3d(self.parent, (nlay, nrow, ncol), np.float32,
                              thickness, name='dz',
                              locat=self.unit_number[0])

        if perlen is not None:
            self.perlen = Util2d(self.parent, (nper,), np.float32, perlen,
                                  name='perlen',
                                  locat=self.unit_number[0])
        else:
            self.perlen = Util2d(self.parent, (nper,), np.float32,
                                  self.parent.mf.dis.perlen.get_value(),
                                  name='perlen',
                                  locat=self.unit_number[0])

        if nstp is not None:
            self.nstp = Util2d(self.parent, (nper,), np.int, nstp,
                                name='nstp',
                                locat=self.unit_number[0])
        else:
            self.nstp = Util2d(self.parent, (nper,), np.int,
                                self.parent.mf.dis.nstp.get_value(),
                                name='nstp',
                                locat=self.unit_number[0])

        if tsmult is not None:
            self.tsmult = Util2d(self.parent, (nper,), np.float32, tsmult,
                                  name='tsmult',
                                  locat=self.unit_number[0])
        else:
            self.tsmult = Util2d(self.parent, (nper,), np.float32,
                                  self.parent.mf.dis.tsmult.get_value(),
                                  name='tsmult',
                                  locat=self.unit_number[0])

        self.laycon = None
        if laycon is not None:
            self.laycon = Util2d(self.parent, (nlay,), np.int, laycon,
                                  name='laycon',
                                  locat=self.unit_number[0])
        else:
            flow_package = self.parent.mf.get_package('BCF6')
            if flow_package is not None:
                self.laycon = Util2d(self.parent, (nlay,), np.int,
                                      flow_package.laycon.get_value(),
                                      name='laycon',
                                      locat=self.unit_number[0])
            else:
                flow_package = self.parent.mf.get_package('LPF')
                if flow_package is not None:
                    self.laycon = Util2d(self.parent, (nlay,),
                                          np.int, flow_package.laytyp.get_value(),
                                          name='laycon', locat=self.unit_number[0])

        s = 'BTN warning. Laycon has not been set.  A modflow model with a '
        s += ' BCF or LPF package does not exist and laycon was not passed '
        s += ' to the BTN constructor.  Setting laycon to 1 (convertible).'
        if self.laycon is None:
            warnings.warn(s)
            self.laycon = Util2d(self.parent, (nlay,), np.int, 1,
                                  name='laycon',
                                  locat=self.unit_number[0])
        return

    def write_file(self):
        """
        Write the package file

        Returns
        -------
        None

        """
        # Open file for writing
        f_btn = open(self.fn_path, 'w')

        # A1,2
        f_btn.write('#{0:s}\n#{1:s}\n'.format(self.heading1, self.heading2))

        # A3
        f_btn.write('{0:10d}{1:10d}{2:10d}{3:10d}{4:10d}{5:10d}\n'
                    .format(self.nlay, self.nrow, self.ncol, self.nper,
                            self.ncomp, self.mcomp))

        # A4
        f_btn.write('{0:4s}{1:4s}{2:4s}\n' \
                    .format(self.tunit, self.lunit, self.munit))

        # A5
        if (self.parent.adv != None):
            f_btn.write('{0:2s}'.format('T'))
        else:
            f_btn.write('{0:2s}'.format('F'))
        if (self.parent.dsp != None):
            f_btn.write('{0:2s}'.format('T'))
        else:
            f_btn.write('{0:2s}'.format('F'))
        if (self.parent.ssm != None):
            f_btn.write('{0:2s}'.format('T'))
        else:
            f_btn.write('{0:2s}'.format('F'))
        if (self.parent.rct != None):
            f_btn.write('{0:2s}'.format('T'))
        else:
            f_btn.write('{0:2s}'.format('F'))
        if (self.parent.gcg != None):
            f_btn.write('{0:2s}'.format('T'))
        else:
            f_btn.write('{0:2s}'.format('F'))
        f_btn.write('\n')

        # A6
        self.laycon.set_fmtin('(40I2)')
        f_btn.write(self.laycon.string)

        # A7
        f_btn.write(self.delr.get_file_entry())

        # A8
        f_btn.write(self.delc.get_file_entry())

        # A9
        f_btn.write(self.htop.get_file_entry())

        # A10
        f_btn.write(self.dz.get_file_entry())

        # A11
        f_btn.write(self.prsity.get_file_entry())

        # A12
        f_btn.write(self.icbund.get_file_entry())

        # A13
        # Starting concentrations
        for s in range(len(self.sconc)):
            f_btn.write(self.sconc[s].get_file_entry())

        # A14
        f_btn.write('{0:10.0E}{1:10.4f}\n' \
                    .format(self.cinact, self.thkmin))

        # A15
        f_btn.write('{0:10d}{1:10d}{2:10d}{3:10d}' \
                    .format(self.ifmtcn, self.ifmtnp, self.ifmtrf, self.ifmtdp))
        if (self.savucn == True):
            ss = 'T'
        else:
            ss = 'F'
        f_btn.write('{0:>10s}\n'.format(ss))

        # A16, A17
        if self.timprs is None:
            f_btn.write('{0:10d}\n'.format(self.nprs))
        else:
            f_btn.write('{0:10d}\n'.format(len(self.timprs)))
            timprs = Util2d(self.parent, (len(self.timprs),),
                             np.float32, self.timprs, name='timprs',
                             fmtin='(8G10.4)')
            timprs.format.fortran = '(8G10.4)'
            f_btn.write(timprs.string)

        # A18, A19
        if self.obs is None:
            f_btn.write('{0:10d}{1:10d}\n'.format(0, self.nprobs))
        else:
            nobs = self.obs.shape[0]
            f_btn.write('{0:10d}{1:10d}\n'.format(nobs, self.nprobs))
            for r in range(nobs):
                f_btn.write('{0:10d}{1:10d}{2:10d}\n' \
                            .format(self.obs[r, 0], self.obs[r, 1],
                                    self.obs[r, 2]))

        # A20 CHKMAS, NPRMAS
        if (self.chkmas == True):
            ss = 'T'
        else:
            ss = 'F'
        f_btn.write('{0:>10s}{1:10d}\n'.format(ss, self.nprmas))


        # A21, 22, 23 PERLEN, NSTP, TSMULT
        for t in range(self.nper):
            s = '{0:10.4G}{1:10d}{2:10.4G}'.format(self.perlen[t],
                                                     self.nstp[t],
                                                     self.tsmult[t])
            if self.ssflag is not None:
                s += ' ' + self.ssflag[t]
            s += '\n'
            f_btn.write(s)
            f_btn.write('{0:10.4G}{1:10d}{2:10.4G}{3:10.4G}\n'
                        .format(self.dt0[t], self.mxstrn[t],
                                self.ttsmult[t], self.ttsmax[t]))
        f_btn.close()
        return

    @staticmethod
    def load(f, model, ext_unit_dict=None):
        if not hasattr(f, 'read'):
            filename = f
            f = open(filename, 'r')

        # A1
        if model.verbose:
            print('   loading COMMENT LINES A1 AND A2...')
        line = f.readline()
        if model.verbose:
            print('A1: '.format(line.strip()))

        # A2
        line = f.readline()
        if model.verbose:
            print('A2: '.format(line.strip()))

        # A3
        if model.verbose:
            print('   loading NLAY, NROW, NCOL, NPER, NCOMP, MCOMP...')
        line = f.readline()
        nlay = int(line[0:10])
        nrow = int(line[11:20])
        ncol = int(line[21:30])
        nper = int(line[31:40])
        try:
            ncomp = int(line[41:50])
        except:
            ncomp = 1
        try:
            mcomp = int(line[51:60])
        except:
            mcomp = 1
        if model.verbose:
            print('   NLAY {}'.format(nlay))
            print('   NROW {}'.format(nrow))
            print('   NCOL {}'.format(ncol))
            print('   NPER {}'.format(nper))
            print('   NCOMP {}'.format(ncomp))
            print('   MCOMP {}'.format(mcomp))

        if model.verbose:
            print('   loading TUNIT, LUNIT, MUNIT...')
        line = f.readline()
        tunit = line[0:4]
        lunit = line[4:8]
        munit = line[8:12]
        if model.verbose:
            print('   TUNIT {}'.format(tunit))
            print('   LUNIT {}'.format(lunit))
            print('   MUNIT {}'.format(munit))

        if model.verbose:
            print('   loading TRNOP...')
        trnop = f.readline()[:20].strip().split()
        if model.verbose:
            print('   TRNOP {}'.format(trnop))

        if model.verbose:
            print('   loading LAYCON...')
        laycon = np.empty((nlay), np.int)
        laycon = read1d(f, laycon)
        if model.verbose:
            print('   LAYCON {}'.format(laycon))

        if model.verbose:
            print('   loading DELR...')
        delr = Util2d.load(f, model, (ncol, 1), np.float32, 'delr',
                            ext_unit_dict)
        if model.verbose:
            print('   DELR {}'.format(delr))

        if model.verbose:
            print('   loading DELC...')
        delc = Util2d.load(f, model, (nrow, 1), np.float32, 'delc',
                            ext_unit_dict)
        if model.verbose:
            print('   DELC {}'.format(delc))

        if model.verbose:
            print('   loading HTOP...')
        htop = Util2d.load(f, model, (nrow, ncol), np.float32, 'htop',
                            ext_unit_dict)
        if model.verbose:
            print('   HTOP {}'.format(htop))

        if model.verbose:
            print('   loading DZ...')
        dz = Util3d.load(f, model, (nlay, nrow, ncol), np.float32, 'dz',
                          ext_unit_dict)
        if model.verbose:
            print('   DZ {}'.format(dz))

        if model.verbose:
            print('   loading PRSITY...')
        prsity = Util3d.load(f, model, (nlay, nrow, ncol), np.float32, 'prsity',
                              ext_unit_dict)
        if model.verbose:
            print('   PRSITY {}'.format(prsity))

        if model.verbose:
            print('   loading ICBUND...')
        icbund = Util3d.load(f, model, (nlay, nrow, ncol), np.int, 'icbund',
                              ext_unit_dict)
        if model.verbose:
            print('   ICBUND {}'.format(icbund))

        if model.verbose:
            print('   loading SCONC...')
        kwargs = {}
        sconc = Util3d.load(f, model, (nlay, nrow, ncol), np.float32, 'sconc1',
                             ext_unit_dict)
        if ncomp > 1:
            for icomp in range(2, ncomp + 1):
                name = "sconc" + str(icomp)
                if model.verbose:
                    print('   loading {}...'.format(name))
                u3d = Util3d.load(f, model, (nlay, nrow, ncol), np.float32,
                                   name, ext_unit_dict)
                kwargs[name] = u3d
        if model.verbose:
            print('   SCONC {}'.format(sconc))

        if model.verbose:
            print('   loading CINACT, THCKMIN...')
        line = f.readline()
        cinact = float(line[0:10])
        try:
            thkmin = float(line[10:20])
        except:
            thkmin = 0.01
        if model.verbose:
            print('   CINACT {}'.format(cinact))
            print('   THKMIN {}'.format(thkmin))

        if model.verbose:
            print('   loading IFMTCN, IFMTNP, IFMTRF, IFMTDP, SAVUCN...')
        line = f.readline()
        ifmtcn = int(line[0:10])
        ifmtnp = int(line[10:20])
        ifmtrf = int(line[20:30])
        ifmtdp = int(line[30:40])
        savucn = False
        if 't' in line[40:50].lower():
            savucn = True
        if model.verbose:
            print('   IFMTCN {}'.format(ifmtcn))
            print('   IFMTNP {}'.format(ifmtnp))
            print('   IFMTRF {}'.format(ifmtrf))
            print('   IFMTDP {}'.format(ifmtdp))
            print('   SAVUCN {}'.format(savucn))

        if model.verbose:
            print('   loading NPRS...')
        line = f.readline()
        nprs = int(line[0:10])
        if model.verbose:
            print('   NPRS {}'.format(nprs))

        timprs = None
        if nprs > 0:
            if model.verbose:
                print('   loading TIMPRS...')
            timprs = np.empty((nprs), dtype=np.float32)
            read1d(f, timprs)
            if model.verbose:
                print('   TIMPRS {}'.format(timprs))

        if model.verbose:
            print('   loading NOBS, NPROBS...')
        line = f.readline()
        nobs = int(line[0:10])
        try:
            nprobs = int(line[10:20])
        except:
            nprobs = 1
        if model.verbose:
            print('   NOBS {}'.format(nobs))
            print('   NPROBS {}'.format(nprobs))

        obs = None
        if nobs > 0:
            if model.verbose:
                print('   loading KOBS, IOBS, JOBS...')
            obs = []
            for l in range(nobs):
                line = f.readline()
                k = int(line[0:10])
                i = int(line[10:20])
                j = int(line[20:30])
                obs.append([k, i, j])
            obs = np.array(obs)
            if model.verbose:
                print('   OBS {}'.format(obs))

        if model.verbose:
            print('   loading CHKMAS, NPRMAS...')
        line = f.readline()
        chkmas = False
        if 't' in line[0:10].lower():
            chkmas = True
        try:
            nprmas = int(line[10:20])
        except:
            nprmas = 1
        if model.verbose:
            print('   CHKMAS {}'.format(chkmas))
            print('   NPRMAS {}'.format(nprmas))


        if model.verbose:
            print('   loading PERLEN, NSTP, TSMULT, TSLNGH, DT0, MXSTRN, TTSMULT, TTSMAX...')
        dt0, mxstrn, ttsmult, ttsmax = [], [], [], []
        perlen = []
        nstp = []
        tsmult = []
        tslngh = []
        ssflag = []
        for kper in range(nper):
            line = f.readline()
            perlen.append(float(line[0:10]))
            nstp.append(int(line[10:20]))
            tsmult.append(float(line[20:30]))
            sf = ' '
            ll = line[30:].strip().split()
            if len(ll) > 0:
                if 'sstate' in ll[0].lower():
                    sf = 'SState'
            ssflag.append(sf)

            if tsmult[-1] < 0:
                t = np.empty((nstp[-1]), dtype=np.float32)
                read1d(f, t)
                tslngh.append(t)
                raise Exception("tsmult <= 0 not supported")

            line = f.readline()
            dt0.append(float(line[0:10]))
            mxstrn.append(int(line[10:20]))
            ttsmult.append(float(line[20:30]))
            ttsmax.append(float(line[30:40]))

        if model.verbose:
            print('   PERLEN {}'.format(perlen))
            print('   NSTP {}'.format(nstp))
            print('   TSMULT {}'.format(tsmult))
            print('   SSFLAG {}'.format(ssflag))
            print('   TSLNGH {}'.format(tslngh))
            print('   DT0 {}'.format(dt0))
            print('   MXSTRN {}'.format(mxstrn))
            print('   TTSMULT {}'.format(ttsmult))
            print('   TTSMAX {}'.format(ttsmax))

        # Close the file
        f.close()

        btn = Mt3dBtn(model, nlay=nlay, nrow=nrow, ncol=ncol, nper=nper,
                      ncomp=ncomp, mcomp=mcomp, tunit=tunit,
                      laycon=laycon, delr=delr, delc=delc, htop=htop, dz=dz,
                      lunit=lunit, munit=munit, prsity=prsity, icbund=icbund,
                      sconc=sconc, cinact=cinact, thkmin=thkmin,
                      ifmtcn=ifmtcn, ifmtnp=ifmtnp, ifmtrf=ifmtrf,
                      ifmtdp=ifmtdp, savucn=savucn, nprs=nprs,
                      timprs=timprs, obs=obs, nprobs=nprobs, chkmas=chkmas,
                      nprmas=nprmas, perlen=perlen, nstp=nstp, tsmult=tsmult,
                      ssflag=ssflag, dt0=dt0, mxstrn=mxstrn, ttsmult=ttsmult,
                      ttsmax=ttsmax, **kwargs)
        return btn
