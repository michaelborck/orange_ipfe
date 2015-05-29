"""
<name>Sign Segment</name>
<description>Widget description</description>
<icon>icons/signsegment.png</icon>
<contact>Widget Author (widget(@at@)author.com)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from OWWidget import *
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.data import camera
from skimage import io
from skimage.morphology import square, diamond, rectangle, disk
from ipfe.segment import local_max_region
import matplotlib.pyplot as plt
import numpy as np
import os

class OWSignSegment(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWSignSegment, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images, Default),
                       ('Response', list, self.process_response)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.images = None
        self.in_images = None
        self.in_response = None
        self.result = None


        # Methods this widget implements.
        self.method = [("Local Max", self.regions),
                       ("Others", self.soon)]

        # Threshold
        self.threshold = 55


        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # Methods Attributes
        # Attributes for methods that have settings/options
        # Opening/CLosing/Erode/Dilate share
        self.neighbourhood_names = [('Square', square), (
            'Diamond', diamond), ('Rectangle', rectangle), ('Disk', disk)]
        self.neighbourhood_id = 0
        self.neighbourhood_size = 3  # width or radius
        self.neighbourhood_height = 3

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Method')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                       callback=[self.show_if, self.update_images, self.apply_if])

        self.option_seperator = OWGUI.separator(self.controlArea)

        # Specify Value
        self.threshold_box = OWGUI.widgetBox(self.controlArea, 'Options')
        OWGUI.hSlider(self.threshold_box, self, "threshold",
                      "Threshold:", 0, 100, 1, callback=[self.update_images, self.apply_if])
        # Dilate options
        names = [x[0] for x in self.neighbourhood_names]
        OWGUI.radioButtonsInBox(
            self.threshold_box, self, "neighbourhood_id", names,
            callback=[self.show_if, self.update_images, self.apply_if])  # , self.show_copy])
        OWGUI.hSlider(self.threshold_box, self, "neighbourhood_size",
                      "Width/Radius:", 1, 40, 1, callback=[self.update_images, self.apply_if])
        self.spin = OWGUI.hSlider(
            self.threshold_box, self, "neighbourhood_height",
            "Height:", 1, 40, 1, callback=[self.update_images, self.apply_if])

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface
        # Median Filter GUI
        self. _box = OWGUI.widgetBox(self.controlArea, '')

        OWGUI.separator(self.controlArea)
        box = OWGUI.widgetBox(self.controlArea, 'Apply Changes')
        apply_button = OWGUI.button(box, self, 'Apply', callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, 'auto_apply', 'Apply changes automatically')
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, 'settings_changed', self.apply)

        OWGUI.rubber(self.controlArea)
        # Make sure GUI is consistent with settings

    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 0:  # WHAT IS THIS!
            self.threshold_box.show()
            self.null_option_box.hide()
        else:
            self.option_seperator.hide()
            self.threshold_box.hide()
            self.null_option_box.show()  # Makes widget behaviour consistent

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.settings_changed = False

    def process_images(self, images):
        self.in_images = images
        self.process_images_and_response()

    def process_response(self, images):
        self.in_response = images
        self.process_images_and_response()

    def process_images_and_response(self):
        self.images = []
        if (self.in_images is not None) and (self.in_response is not None):
            method = self.method[self.method_id][1]
            rois = [method(image.data, response.data) for
                    (image, response) in zip(self.in_images, self.in_response)]
            for roi in rois[0]:
                self.images.append(OrangeImage(roi))
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.in_images))
            self.apply_if()

    def update_images(self):
        self.process_images_and_response()

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.

    # The following method performs any necessary pre/post-processing.
    def regions(self, image, response):
        shape = self.neighbourhood_names[self.neighbourhood_id][1]
        if self.neighbourhood_id == 2:  # rectangle
            return local_max_region(image, response, self.threshold,
                    shape(self.neighbourhood_size, self.neighbourhood_height))
        else:
            return local_max_region(image, response, self.threshold,
                    shape(self.neighbourhood_size))

    def soon(self, images, response):
        return [camera()]

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWSignSegment()
    ow.show()
    #image = OrangeImage(io.imread("theimage.jpg"))
    #ow.process_images([image])
    #response = OrangeImage(io.imread("theresponse.png"))
    #ow.process_response([response])
    appl.exec_()
