"""
<name>Exposure</name>
<description></description>
<icon>icons/exposure.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.exposure import equalize_hist
import numpy as np
from pymorph import regmax, regmin, overlay
from scipy.ndimage import label
from skimage import img_as_ubyte
from skimage.exposure import rescale_intensity, equalize_hist,\
        equalize_adapthist, adjust_sigmoid, adjust_log, adjust_gamma
import matplotlib.pyplot as plt
from ipfe.exposure import contrast_stretch


class OWExposure(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']
    def __init__(self, parent=None, signalManager=None):
        super(OWExposure, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements
        self.method = [('Gamma Correction', self.gamma),
                       ('Log Correction', self.log),
                       ('Sigmoid Correction', self.sigmoid),
                       ('CLAHE', self.clahe),
                       ('Hist Equalization', self.hist_equal),
                       ('Rescale Intensity', self.rescale),
                       ('Contrast Stretch', self.stretch)
                       ]

        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()


        # Methods Attributes
        self.gamma = 1
        self.log_gain = 1
        self.sigmoid_gain = 1
        self.cutoff = 1

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Options')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                callback=[self.update_images, self.show_if])

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface

        # Gamma Correction
        self.gamma_box = OWGUI.widgetBox(self.controlArea, 'Gamma Correction')
        OWGUI.spin(self.gamma_box, self, 'gamma', min=0, max=30, step=5,
                   label='Gamma:', callback=[self.show_if, self.update_images, self.apply_if])

        # Log Correction
        self.log_box = OWGUI.widgetBox(self.controlArea, 'Log Correction')
        OWGUI.spin(self.log_box, self, 'log_gain', min=0, max=30, step=5,
                   label='Log Gain:', callback=[self.show_if, self.update_images, self.apply_if])

        # Sigmoid Correction
        self.sigmoid_box = OWGUI.widgetBox(self.controlArea, 'Sigmoid Correction')
        OWGUI.spin(self.sigmoid_box, self, 'cutoff', min=0, max=30, step=5,
                   label='Cutoff:', callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.spin(self.sigmoid_box, self, 'sigmoid_gain', min=0, max=30, step=5,
                   label='Gain:', callback=[self.show_if, self.update_images, self.apply_if])


        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Apply Changes')
        apply_button = OWGUI.button(box, self, 'Apply', callback = self.apply)
        auto_apply_cb = OWGUI.checkBox(box, self, 'auto_apply', 'Apply changes automatically')
        OWGUI.setStopper(self, apply_button, auto_apply_cb, 'settings_changed', self.apply)


        OWGUI.rubber(self.controlArea)
        # Make sure GUI is consistent with settings
        self.show_if()


    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 0: # gamma
            self.null_option_box.hide()
            self.gamma_box.show()
            self.log_box.hide()
            self.sigmoid_box.hide()
        elif self.method_id == 1: # log
            self.null_option_box.hide()
            self.gamma_box.hide()
            self.log_box.show()
            self.sigmoid_box.hide()
        elif self.method_id == 2: # sigmoid
            self.null_option_box.hide()
            self.gamma_box.hide()
            self.log_box.hide()
            self.sigmoid_box.show()
        else:
            self.gamma_box.hide()
            self.log_box.hide()
            self.sigmoid_box.hide()
            self.option_seperator.hide()
            self.null_option_box.show() # Makes widget behaviour consistent

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.settings_changed = False

    def process_images(self, images):
        self.data = images
        if images != None:
            method = self.method[self.method_id][1]
            self.images = [OrangeImage(method(image.data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)


    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.

    def gamma(self, image):
        return adjust_gamma(image,self.gamma)

    def log(self, image):
        return adjust_log(image,self.log_gain)

    def sigmoid(self, image):
        return adjust_sigmoid(image,self.cutoff, self.sigmoid_gain)

    def clahe(self, image):
        return equalize_adapthist(image)

    def hist_equal(self, image):
        return equalize_hist(image)

    def rescale(self, image):
        return rescale_intensity(image)

    def stretch(self, image):
        return contrast_stretch(image)


if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWExposure()
    ow.show()
    appl.exec_()
