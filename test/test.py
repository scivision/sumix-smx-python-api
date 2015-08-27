#!/usr/bin/env python
from numpy.testing import assert_array_equal
from numpy import array,uint8
from demosaic import demosaic
#%% global
testimg = array([[23,128],
                [202,27],],dtype=uint8)
#%% test raw->color, nearest neighbor
def test_demosaic_color():
# we make it artifically 1 frame of a series
    testnear = demosaic(testimg[None,:,:],'',1,color=True)

    refnear = array([[[128,25,202],
                      [128,25,202]],
                     [[128,25,202],
                      [128,25,202]]], dtype=testimg.dtype)[None,:,:]

    assert_array_equal(testnear,refnear)
    assert testimg.dtype == testnear.dtype
#%% test raw->mono, nearest neighbor
def test_demosaic_gray():
    testnear = demosaic(testimg[None,:,:],'',1,color=False)

    refnear = array([[76,76],
                        [76,76]], dtype=testimg.dtype)[None,:,:]

    assert_array_equal(testnear,refnear)
    assert testimg.dtype == testnear.dtype
#%% rgb2gray
def test_rgb2gray():
    from rgb2gray import rgb2gray
    #RGBA test image
    rgba = array([[[[  76.,   76.,   76.,  255.],
                        [  76.,   76.,   76.,  255.]],
                       [[  76.,   76.,   76.,  255.],
                         [  76.,   76.,   76.,  255.]]]],dtype=uint8)

    testgray =  rgb2gray(rgba)
    refalpha = array([[76,76],
                        [76,76]], dtype=rgba.dtype)[None,:,:]
    assert_array_equal(testgray,refalpha)

if __name__ == '__main__':
    test_demosaic_color()
    test_demosaic_gray()
    test_rgb2gray()