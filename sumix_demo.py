#!/usr/bin/python3
"""
Demonstrator of Sumix camera
michael@scivision.co
GPLv3+ license
to stop free run demo, on Windows press <esc> or <space> when focused on terminal window
    on Linux, press <ctrl> c (sigint)
"""
from numpy import uint8, empty
from os.path import splitext,expanduser
from platform import system
import sys
#
from sumixapi import Camera
from demosaic import demosaic
platf = system().lower()
if platf=='windows':
    from msvcrt import getwch, kbhit
    windows = True
else:
    windows = False

def main(w,h,nframe,expos, decim, color, tenbit, preview, verbose=False):
#%% setup camera class
    cam = Camera(w,h,decim,tenbit,verbose=verbose) # creates camera object and opens connection

    if verbose:
        if cam.info.SensorType==0:
            print('camera is black and white')
        elif cam.info.SensorType==1:
            print('camera is color')
        cdetex = cam.getCameraInfoEx()
        print(cdetex.HWModelID, cdetex.HWVersion, cdetex.HWSerial)
#%% sensor configuration
    cam.setFrequency(1)     #set to 24MHz (fastest)
    if verbose:
        print('camera sensor frequency ' + str(cam.getFrequency())) #str() in case it's NOne

    if expos is not None and 0.2 < expos < 10000: #need short circuit
        if verbose:
            emin,emax = cam.getExposureMinMax()
            print('camera exposure min, max [ms] = {:0.3f}'.format(emin) + ', {:0.1f}'.format(emax))
        cam.setExposure(expos)
    exptime = cam.getExposure()
    print('exposure is {:0.3f}'.format(exptime) + ' ms.')
#%% setup figure (for loter plotting)
    if preview:
        figure(1).clf(); fgrw = figure(1);  axrw = fgrw.gca()
        hirw = axrw.imshow(empty((cam.ypix,cam.xpix), dtype=uint8),
                           origin='upper', #this is consistent with Sumix chip and tiff
                           vmin=0, vmax=256, cmap='gray')
    else:
        hirw = None
#%% start acquisition
    cam.startStream()
    if nframe is None:
        frames = freewheel(cam, color,hirw)
    elif 0 < nframe < 200:
        frames =fixedframe(nframe,cam, color,hirw)
    else:
        exit('*** I dont know what to do with nframe=' + str(nframe))
#%% shutdown camera
    cam.stopStream()

    return frames
#%% ===========================
def freewheel(cam, color,hirw):
    try:
        while True:
            frame = cam.grabFrame()

            if color:
                frame = demosaic(frame, 'ours')

            if hirw is not None:
                hirw.set_data(frame.astype(uint8))
                draw(); pause(0.001)

            if windows and kbhit():
                keyputf = getwch()
                if keyputf == u'\x1b' or keyputf == u' ':
                    print('halting acquisition due to user keypress')
                    break

    except KeyboardInterrupt:
        print('halting acquisition')

    return frame

def fixedframe(nframe,cam, color,hirw):
    if color:
        frames = empty((nframe,cam.ypix,cam.xpix,3), dtype=uint8)
    else:
        frames = empty((nframe,cam.ypix,cam.xpix), dtype=uint8)

    try:
        for i in range(nframe):
            frame = cam.grabFrame()

            if color:
                frames[i,...] = demosaic(frame, 'ours', color=color)
            else:
                frames[i,...] = frame

            if hirw is not None:
                hirw.set_data(frames[i,...].astype(uint8))
                #hirw.cla()
                #hirw.imshow(dframe)
                draw(); pause(0.001)
    except KeyboardInterrupt:
        print('halting acquisition per user Ctrl-C')

    return frames

def saveframes(ofn,frames,color):
    if ofn is not None and frames is not None:
        ext = splitext(expanduser(ofn))[1].lower()
        if ext[:4] == '.tif':
            try:
                import tifffile
            except ImportError:
                print('please install tifffile via typing in Terminal:    pip install tifffile')
                print('doing a last-resort dump to disk in "pickle" format, read with numpy.load')
                frames.dump(ofn)

            print('tifffile write ' + ofn)

            pho = 'rgb' if color else 'minisblack'

            tifffile.imsave(ofn,frames,compress=6,
                        photometric=pho,
                        description='my Sumix data',
                        extratags=[(65000,'s',None,'My custom tag #1',True),
                                   (65001,'s',None,'My custom tag #2',True),
                                   (65002,'f',2,[123456.789,9876.54321],True)])

        elif ext == '.h5':
            try:
                import h5py
            except ImportError:
                print('please install h5py via typing in Terminal: pip install h5py')
                print('doing a last-resort dump to disk in "pickle" format, read with numpy.load')
                frames.dump(ofn)

            with h5py.File(ofn,libver='latest') as f:
                f.create_dataset('/images',data=frames,compression='gzip')
#%%
if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description="Sumix Camera demo")
    p.add_argument('-c','--color',help='use Bayer demosaic for color camera (display only, disk writing is raw)',action='store_true')
    p.add_argument('-d','--decim',help='decimation (binning)',type=int,default=None)
    p.add_argument('-e','--exposure',help='exposure set [ms]',type=float,default=None)
    p.add_argument('-n','--nframe',help='number of images to acquire',type=int,default=None)
    p.add_argument('-f','--file',help='name of tiff file to save (non-demosaiced)',type=str,default=None)
    p.add_argument('-x','--width',help='width in pixels of ROI',type=int,default=None)
    p.add_argument('-y','--height',help='height in pixels of ROI',type=int,default=None)
    p.add_argument('-t','--tenbit',help='selects 10-bit data mode (default 8-bit)',action='store_true')
    p.add_argument('-p','--preview',help='shows live preview of images acquired',action='store_true')
    p.add_argument('-v','--verbose',help='more verbose feedback to user console',action='store_true')
    a = p.parse_args()

    if a.preview:
        from matplotlib.pyplot import figure,draw,pause#, show

    frames = main(a.width,a.height, a.nframe, a.exposure, a.decim, a.color, a.tenbit, a.preview, a.verbose)

    saveframes(a.file,frames,a.color)
