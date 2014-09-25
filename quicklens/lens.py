# quicklens/lens.py
# --
# this module contains subroutines for applying the lensing operation to flat-sky maps.

import numpy as np
import scipy.interpolate
import scipy.misc

import maps
import qest

def calc_lensed_b_first_order( e, phi ):
    """ evaluate the lensed B-mode to first-order in phi on the flat-sky.
         * e   = unlensed E-modes (either a maps.rmap, maps.rfft, or maps.cfft object).
         * phi = cmb lensing potential (either a maps.rmap, maps.rfft, or maps.cfft object).

        returns a maps.cfft object containing the lensed B-modes to first-order in phi.
    """
    if maps.is_rmap(e):
        e = e.get_rfft().get_cfft()
    if maps.is_rfft(e):
        e = e.get_cfft()

    if maps.is_rmap(phi):
        pfft = phi.get_rfft().get_cfft()
    elif maps.is_rfft(phi):
        pfft = phi.get_cfft()
    else:
        pfft = phi
        
    assert( e.compatible(pfft) )

    ret = maps.cfft(nx=e.nx, dx=e.dx, ny=e.ny, dy=e.dy)

    lx, ly  = ret.get_lxly()
    l       = np.sqrt(lx**2 + ly**2)
    psi     = np.arctan2(lx, -ly)

    ret.fft = -0.5j * ( np.fft.fft2( +np.fft.ifft2(lx*e.fft*np.exp(+2.j*psi)) * np.fft.ifft2(lx*pfft.fft) +
                                     +np.fft.ifft2(ly*e.fft*np.exp(+2.j*psi)) * np.fft.ifft2(ly*pfft.fft) ) * np.exp(-2.j*psi) +
                        np.fft.fft2( -np.fft.ifft2(lx*e.fft*np.exp(-2.j*psi)) * np.fft.ifft2(lx*pfft.fft) +
                                     -np.fft.ifft2(ly*e.fft*np.exp(-2.j*psi)) * np.fft.ifft2(ly*pfft.fft) ) * np.exp(+2.j*psi) )
    ret    *= np.sqrt(ret.nx * ret.ny) / np.sqrt(ret.dx * ret.dy)
    return ret

def calc_lensed_clbb_flat_sky_first_order(lbins, nx, dx, cl_unl, w=None):
    """ evaluate the lensed B-mode power spectrum at first order in |phi|^2 on the flat-sky.
         * lbins  = array or list containing boundaries for the binned return spectrum.
         * nx     = width of the grid (in pixels) used to peform the calculation.
         * dx     = width of each pixel (in radians) used to perform the calculation.
         * cl_unl = object with attributes
                      .lmax = maximum multipole
                      .clee = unlensed E-mode power spectrum
                      .clpp = lensing potential power spectrum
         * (optional) w = weight function w(l) to be used when binning the return spectrum.

         returns a spec.bcl object containing the binned clbb power spectrum.
    """
    ret = maps.cfft(nx, dx)
    qeep = qest.lens.blen_EP( np.sqrt(cl_unl.clee), np.sqrt(cl_unl.clpp) )
    qeep.fill_resp( qeep, ret, np.ones(cl_unl.lmax+1), 2.*np.ones(cl_unl.lmax+1), npad=1 )
    return ret.get_ml(lbins, w=w)

def calc_lensed_clbb_flat_sky_first_order_curl(lbins, nx, dx, cl_unl, w=None):
    """ version of calc_lensed_clbb_flat_sky_first_order which treats cl_unl as a curl-mode lensing potential psi rather than as a gradient mode phi. """
    ret = maps.cfft(nx, dx)
    qeep = qest.qest_blm_EX( np.sqrt(cl_unl.clee), np.sqrt(cl_unl.clpp) )
    qeep.fill_resp( qeep, ret, np.ones(cl_unl.lmax+1), 2.*np.ones(cl_unl.lmax+1) )
    return ret.get_ml(lbins, w=w)
