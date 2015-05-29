"""
<name>Filter</name>
<description>Apply a filter to images.  Current filters include Gabor,... </description>
<icon>icons/filter.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange  # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage

from ipfe.features import patch_Gabor
from scipy import ndimage
from mahotas import haar, ihaar, daubechies, idaubechies


class OWFilter(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWFilter, self).__init__(parent, signalManager)

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
        self.method = [('Harr', self.haar),
                       ('Inverse Harr', self.ihaar),
                       ("Daubechiles", self.daubechies),
                       ('Inverse Daubechiles', self.idaubechies),
                       ('Gabor', self.gabor)]

        # Attributes for methods that have settings/options

        # Gabor Options
        self.gb_sigma = 5
        self.gb_lambd = 50
        self.gb_theta = 0
        self.gb_psi = 90
        self.gb_kernel_size = 21

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
        # Gabor GUI
        self.gb_box = OWGUI.widgetBox(self.controlArea, 'Gabor Options')
        #OWGUI.hSlider(I
            #self.gb_box, self, "gb_kernel_size", "Size of Gabor kernel", 1, 21, 10,
            #callback=self.update_images)
        #OWGUI.hSlider(
            #self.gb_box, self, "gb_sigma", "Sigma of gaussian envelope", 3, 68, 10,
            #callback=self.update_images)
        OWGUI.hSlider(
            self.gb_box, self, "gb_theta", "Orientation (degrees)", 0, 180, 90,
            callback=self.update_images)
        #OWGUI.hSlider(
            #self.gb_box, self, "gb_lambd", "Wavelength of sinusodial", 2, 256, 90,
            #callback=self.update_images)
        #OWGUI.hSlider(self.gb_box, self, "gb_psi", "Phase offset", 1, 180, 1,
                      #callback=self.update_images)

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
        if self.method_id == 4:  # Gabor
            self.null_option_box.hide()
            self.gb_box.show()
        else:  # No options/setting box needed
            self.gb_box.hide()
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
    def gabor(self, image):
        image = image.gray().data
        return patch_Gabor(image, self.gb_theta)

    def haar(self, image):
        image = image.gray().data
        return haar(image, 'D2')

    def ihaar(self, image):
        image = image.gray().data
        return ihaar(image, 'D2')

    def daubechies(self, image):
        image = image.gray().data
        return daubechies(image, 'D2')

    def idaubechies(self, image):
        image = image.gray().data
        return idaubechies(image, 'D2')

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWFilter()
    ow.show()
    appl.exec_()
