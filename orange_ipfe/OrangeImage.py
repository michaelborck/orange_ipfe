from scipy.misc import imread, imresize

import numpy as np
from skimage.color import convert_colorspace, gray2rgb, rgb2gray, rgb2lab
from skimage import img_as_float
from qimage2ndarray import array2qimage
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class OrangeImage(object):

    def __init__(self, data=None, colour='RGB', fname="Internal"):
        self.data = data
        self.colour = colour
        self.filename = fname
        # if data != None :
            # self.data = img_as_float(data)

    @classmethod
    def load(cls, filename):
        name = str(filename)
        return OrangeImage(imread(name), fname=name)

    def pixmap(self):
        return QPixmap.fromImage(self.qimage())

    def qimage(self):
        return(array2qimage(self.data, True))

    def rgb(self):
        if self.is_gray():
            return OrangeImage(gray2rgb(self.data), 'RGB')
        else:
            return OrangeImage(convert_colorspace(self.data, self.colour,
                                                  'RGB'), colour='RGB')

    def hsv(self):
        if self.is_gray():
            return OrangeImage(convert_colorspace(gray2rgb(self.data),
                                                  'RGB', 'HSV'), colour='HSV')
        else:
            return OrangeImage(convert_colorspace(self.data, self.colour,
                                                  'HSV'), colour='HSV')

    def lab(self):
        if self.is_gray():
            return OrangeImage(rgb2lab(gray2rgb(self.data)), colour='LAB')
        else:
            return OrangeImage(rgb2lab(self.data), colour='LAB')

    def cie(self):
        if self.is_gray():
            return OrangeImage(convert_colorspace(gray2rgb(self.data),
                                                  'RGB', 'RGB CIE'), colour='RGB CIE')
        else:
            return OrangeImage(convert_colorspace(self.data, self.colour,
                                                  'RGB CIE'), colour='CIE')

    def xyz(self):
        if self.is_gray():
            return OrangeImage(convert_colorspace(gray2rgb(self.data),
                                                  'RGB', 'XYZ'), colour='XYZ')
        else:
            return OrangeImage(convert_colorspace(self.data, self.colour,
                                                  'XYZ'), colour='XYZ')

    def gray(self):
        if self.is_gray():
            return OrangeImage(self.data, colour='GRAY')
        else:
            return OrangeImage(rgb2gray(self.rgb().data), colour='GRAY')

    def is_gray(self):
        return self.data.ndim == 2

    def has_alpha(self):
        return self.data.ndim == 4

    def is_rgb(self):
        return self.colour == 'RGB'

    def is_hsv(self):
        return self.colour == 'HSV'

    def is_lab(self):
        return self.colour == 'LAB'

    def is_cie(self):
        return self.colour == 'RGB CIE'

    def is_xyz(self):
        return self.colour == 'XYZ'

    def thumbnail(self, height=150):
        """
        Crates a thumbnail of the image in the suitable QImage format.
        """
        # Maintain aspect ratio of image
        proportion = float(height) / self.height()
        width = int(self.width() * proportion)

        # misc.imresize will scale image, so convert [0,1] -> [0,255] as uint8
        thumb = (imresize(self.data, (height, width))).astype(np.uint8)
        return(array2qimage(thumb, True))

    def height(self):
        """
        Returns an integer respresenting the image height.
        """
        return self.data.shape[0]

    def width(self):
        """
        Returns an integer respresenting the image width.
        """
        return self.data.shape[1]
