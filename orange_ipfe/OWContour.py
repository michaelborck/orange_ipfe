"""
<name>Contours</name>
<description>Local Binary Pattern
<icon>icons/contours.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from OWWidget import *
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
import skimage.feature as ft
from skimage import io, color
import numpy as np
from skimage import measure
from skimage.transform import rotate, warp
import matplotlib.pyplot as plt


class OWContour(OWImgWidget):
    settingsList = ['auto_apply', 'block_size']

    def __init__(self, parent=None, signalManager=None):
        super(OWContour, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list), ('Data', ExampleTable)]

        # Attributes
        self.data = None
        self.feature = None
        self.images = None

        # Settings attributes
        self.auto_apply = True
        self.settings_changed = False
        self.label = "UNK"
        self.loadSettings()
        self.points = 16
        self.radius = 2
        self.method = 'uniform'

        # Methods Attributes

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        OWGUI.hSlider(self.controlArea, self, "points",
                      "Number of points:", 3, 30, 2, callback=[self.update, self.apply_if])
        OWGUI.hSlider(self.controlArea, self, "radius",
                      "Radius:", 3, 30, 2, callback=[self.update, self.apply_if])
        box = OWGUI.widgetBox(self.controlArea, "Label Class")
        OWGUI.lineEdit(box, self, "label", label="Class:",
                       orientation="horizontal", labelWidth=40,
                       callback=self.update)

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Apply Changes')
        apply_button = OWGUI.button(box, self, 'Apply', callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, 'auto_apply', 'Apply changes automatically')
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, 'settings_changed', self.apply)

        # OWGUI.rubber(self.controlArea)
        # self.update_description()

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.send('Data', self.feature)
        self.settings_changed = False

    def process_images(self, images):
        self.data = images
        self.update_images()
        self.describe_images()

    def update(self):
        self.update_images()
        self.describe_images()

    def update_images(self):
        if self.data != None:
            self.images = [OrangeImage(self.contour(
                color.rgb2gray(image.data))) for image in self.data]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def describe_images(self):
        if self.images != None:
            feature_vector = [self.describe(
                image.data) for image in self.images]
            print feature_vector[0]
            descriptors_and_status = [Orange.feature.Descriptor.make('lbp%i' % x, Orange.feature.Type.Continuous)
                                      for x in range(len(feature_vector[0]) - 1)]
            # Get rid of status codes from the 'make' calls.
            descriptors = [pair[0] for pair in descriptors_and_status]
            # Reuse the 'Label' descriptor
            descriptors.append(Orange.feature.Descriptor.make(
                'Label', Orange.feature.Type.Discrete, ["UNK", "BS", "TL"])[0])
            domain = Orange.data.Domain(descriptors)
            self.feature = Orange.data.Table(domain, feature_vector)
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def contour(self, image):
        contours = measure.find_contours(image, 0.8)
        fig = plt.figure()
        plt.gray()
        # plt.imshow(image, interpolation='nearest')
        for n, contour in enumerate(contours):
            # plt.plot(contour[:,1], contour[:,0], linewidth=2)
            plt.plot(contour[:, 0], contour[:, 1], linewidth=2)

        plt.axis('image')
        plt.xticks([])
        plt.yticks([])
        fig.savefig('foo.png', bbox_inches=0, dpi=fig.dpi)
        fig.savefig('foo.png')
        fig.clf()
        return rotate(io.imread('foo.png'), 270)

    def describe(self, image):
        hist, bins = np.histogram(
            image, normed=True, bins=self.points + 2, range=(0, self.points + 2))
        lbp = hist.tolist()
        lbp.append(str(self.label))
        return lbp

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWContour()
    ow.show()
    appl.exec_()
