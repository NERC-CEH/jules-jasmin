
try:
    from PIL import Image
except:
    import Image

import logging
import numpy as N

log = logging.getLogger(__name__)

def merge(*args):
    finalImg = args[0]
    
    for i in args[1:]:
        finalImg = myCombine(finalImg, i)
    
    return finalImg


def myCombine(baseIm, topIm):

    # Ensure that the images are in RGBA format.
    if baseIm.mode != 'RGBA':
        baseImRgba = baseIm.convert('RGBA')
    else:
        baseImRgba = baseIm

    if topIm.mode != 'RGBA':
        topImRgba = topIm.convert('RGBA')
    else:
        topImRgba = topIm

    # combining the two images using the formula:
    # alpha_out = alpha_top + alpha_base * (1 - alpha_top)
    # colour_out = (colour_top * alpha_top + 
    #              colour_base * alpha_base * (1 - alpha_top) ) / alpha_out
    
    baseArr = N.asarray(baseImRgba, dtype=float)/255
    topArr = N.asarray(topImRgba, dtype=float)/255
    R,G,B,A = 0,1,2,3
    res = N.zeros(baseArr.shape)

    res[:,:,A] = topArr[:,:,A] + baseArr[:,:,A] * (1-topArr[:,:,A])

    for i in [R,G,B]:

        pt1 = topArr[:,:,i] * topArr[:,:,A]
        pt2 = baseArr[:,:,i] * baseArr[:,:,A] * (1-topArr[:,:,A])
        res[:,:,i] = (pt1 + pt2) / res[:,:,A]

    res = res * 255
    res.round()
    res = N.array(res, dtype=N.uint8)

    return Image.fromarray(res, 'RGBA')
