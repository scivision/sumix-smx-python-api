"""
demosaic bayer filter of type 'grbg' using nearest neighbor interpolation
michael@scivision.co
GPLv3+

input:
assumes uint8 or uint16 raw bayer filtered grbg input
assumes 2-D I x J pixels, where a single image is I x J pixels,
        where I and J are both even numbers

output:
same uint8 or uint16 shape as inpout

Note:  If you're on Windows, be sure your PATH environment variable includes your Python DLLs directory.
    E.g. for Anaconda on Windows installed to C:\Anaconda, you should have C:\Anaconda\DLLs on your Windows PATH.

"""
from __future__ import division,absolute_import
import numpy as np
from scipy.ndimage.interpolation import zoom
from warnings import warn
#
from rgb2gray import rgb2gray

"""
you may not have the Sumix API installed. Try the method='ours' to fallback to non-sumix demosaic
"""

def demosaic(img,method='',alg=1,color=True):
    if img is None:
        return None

    ndim = img.ndim
    if ndim==2:
        pass #normal case
    elif ndim==3 and img.shape[-1] != 3: #normal case, iterate
        print('demosaic: iterate over {:d} frames'.format(img.shape[0]))
        if color:
            dem = np.empty(img.shape+(3,),dtype=img.dtype)
        else:
            dem = np.empty(img.shape,dtype=img.dtype)
        for i,f in enumerate(img):
            dem[i,...] = demosaic(f,method,alg,color)
        return dem
    else:
        warn('demosaic: unsure what you want with shape {} so return unmodified'.format(img.shape))
        return img

    if str(method).lower()=='sumix':
        from sumixapi import Convert
        return Convert().BayerToRgb(img,alg)
    else:
        return grbg2rgb(img,alg,color)

def grbg2rgb(img,alg=1,color=True):
    """ GRBG means the upper left corner of the image has four pixels arranged like
    green  red
    blue    green
    """
    if img.ndim !=2:
        warn('demosaic: for now, only 2-D numpy array is accepted  {}'.format(img.shape))
        return None

    if img.shape[0] % 2 or img.shape[1] % 2:
        warn('demosaic: requires even-numbered number of pixels on both axes   {}'.format(img.shape))
        return None

    if not img.dtype in (np.uint8, np.uint16):
        warn('demosaic is currently for uint8 and uint16 input ONLY  {}'.format(img.shape))
        return None

   #upcast g1,g2 to avoid overflow from 8-bit or 16-bit input
    g1 = img[0::2,0::2].astype(np.uint32)
    g2 = img[1::2,1::2].astype(np.uint32)
    r =  img[0::2,1::2]
    b =  img[1::2,0::2]

    g = np.round(((g1+g2) / 2)).astype(img.dtype)

    rgb = np.dstack((r,g,b)) #this is the way matplotlib likes it for imshow (RGB in axis=2)


    if 1<=alg<=4:
        order=alg-1
    else:
        warn('unknown method {}  falling back to nearest neighbor alg=1'.format(alg))
        order=0

    demos = zoom(rgb,(2,2,1),order=order,) #0:nearest neighbor

    if not color:
        demos = rgb2gray(demos)

    return demos
