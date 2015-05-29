"""
<name>Smooth Blur</name>
<description>Smooth the image</description>
<icon>icons/smooth.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange  # Needed to test outside of Orange
import OWGUI
import numpy as np
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.morphology import square, diamond, rectangle, disk
from skimage.filters import gaussian_filter, median


class OWSmooth(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWSmooth, self).__init__(parent, signalManager)

        # Input/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Settings
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # Methods this widget implements.
        self.method = [('Gaussian Blur', self.gaussian),
                       ('Median Blur', self.median)]

        # Attributes for methods that have settings/options
        # Gaussian Options
        self.gau_mode_items = [
            'wrap', 'nearest', 'constant', 'reflect', 'mirror']
        self.gau_sigma = 5
        self.gau_order = 0
        self.gau_mode = 0

        # Median filter Options
        #self.med_mode_items = ['reflect', 'constant', 'nearest', 'mirror']
        #self.med_mode = 0
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

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface
        # Median Filter GUI
        self.med_box = OWGUI.widgetBox(
            self.controlArea, 'Median Filter Options')
        #self.med_mode_sb = OWGUI.comboBox(
            #self.med_box, self, "med_mode", label="Array borders",
            #items=self.med_mode_items, callback=[self.show_if, self.update_images, self.apply_if])
        names = [x[0] for x in self.neighbourhood_names]
        OWGUI.radioButtonsInBox(self.med_box, self, "neighbourhood_id", names,
                                callback=[self.show_if, self.update_images, self.apply_if])  # , self.show_copy])
        OWGUI.hSlider(self.med_box, self, "neighbourhood_size",
                      "Width/Radius:", 1, 10, 1, callback=[self.show_if, self.update_images, self.apply_if])
        self.spin = OWGUI.hSlider(self.med_box, self, "neighbourhood_height",
                                  "Height:", 1, 10, 1, callback=[self.update_images, self.apply_if])

        # Gaussian GUI
        self.gau_box = OWGUI.widgetBox(self.controlArea, 'Gaussisn Options')
        OWGUI.spin(self.gau_box, self, 'gau_sigma', min=0, max=30, step=5,
                   label='Standard Deviation:', callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.comboBox(self.gau_box, self, "gau_mode", label="Array borders",
                       items=self.gau_mode_items, callback=[self.update_images, self.apply_if])

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Apply Changes')
        apply_button = OWGUI.button(box, self, 'Apply', callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, 'auto_apply', 'Apply changes automatically')
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, 'settings_changed', self.apply)

        OWGUI.rubber(self.controlArea)

        # Make sure GUI is consistent with settings
        self.show_if()

    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 0:  # Gaussian
            self.null_option_box.hide()
            self.med_box.hide()
            self.gau_box.show()
        elif self.method_id == 1:  # Median filter
            self.null_option_box.hide()
            self.gau_box.hide()
            self.med_box.show()
            if self.neighbourhood_id == 2:
                self.spin.setEnabled(True)
            else:
                self.spin.setEnabled(False)
        else:  # No options/setting box needed
            self.gau_box.hide()
            self.med_box.hide()
            self.option_seperator.hide()
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
        self.data = images
        if images != None:
            method = self.method[self.method_id][1]
            self.images = [OrangeImage(method(image)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.
    def median(self, image):
        image = image.data
        shape = self.neighbourhood_names[self.neighbourhood_id][1]
        if self.neighbourhood_id == 2:  # rectangle
            image = median(image, shape(self.neighbourhood_size,
                                               self.neighbourhood_height))
        else:
            image = median(image, shape(self.neighbourhood_size))
        return image

    def gaussian(self, image):
        image = image.data
        return gaussian_filter(image, sigma=self.gau_sigma,
                               mode=self.gau_mode_items[self.gau_mode])

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWSmooth()
    ow.show()
    appl.exec_()
