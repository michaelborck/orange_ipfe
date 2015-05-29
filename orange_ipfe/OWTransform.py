"""
<name>Transform</name>
<description>Convert and image from one domain to another e.g. Fourier space or
Hough space.</description>
<icon>icons/transform.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
import numpy as np
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.transform import integral_image, rotate, resize
#from ipamv.transform import fft, distance


class OWTransform(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWTransform, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements
        self.method = [('Integral Image', integral_image),
                       ('Rotation', self.rotate),
                       ('Resize', self.change_size),
                       ('Fourier', self.fft),
                       ('Distance Transform', self.distance)
                       ]

        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # Attributes for methods that have settings/options
        # Resize
        self.resize_rows = 100
        self.resize_cols = 100

        # Rotate
        self.rotate_angle = 45

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        self.option_seperator = OWGUI.separator(self.controlArea)

        # For each method that needs options/setting setup interface
        box = OWGUI.widgetBox(self.controlArea, 'Options')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                       callback=[self.show_if, self.update_images])

        # Resize
        self.resize_box = OWGUI.widgetBox(self.controlArea, 'Resize Options')
        OWGUI.spin(
            self.resize_box, self, 'resize_rows', min=1, max=2048, step=32,
            label='Rows:', callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.spin(
            self.resize_box, self, 'resize_cols', min=1, max=2048, step=32,
            label='Cols:', callback=[self.show_if, self.update_images, self.apply_if])

        # Rotate
        self.rotate_box = OWGUI.widgetBox(self.controlArea, 'Rotate Options')
        OWGUI.spin(
            self.rotate_box, self, 'rotate_angle', min=0, max=360, step=45,
            label='Angle:', callback=[self.show_if, self.update_images, self.apply_if])

        # This is the default "box", so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        # TODO: Test is still needed now using OWGUI.rubber()
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

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
        if self.method_id == 2:  # Resize
            self.null_option_box.hide()
            self.rotate_box.hide()
            self.resize_box.show()
        elif self.method_id == 1:  # Rotate
            self.null_option_box.hide()
            self.resize_box.hide()
            self.rotate_box.show()
        else:
            self.resize_box.hide()
            self.rotate_box.hide()
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
            self.images = [OrangeImage(method(image.data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.
    def change_size(self, image):
        return resize(image, (self.resize_rows, self.resize_cols))

    def rotate(self, image):
        return rotate(image, self.rotate_angle)

    def fft(self, image):
        return (np.log10(fft(image)))

    def distance(self, image):
        return distance(image)
        # image = img_as_float(image)
        # T = threshold_otsu(image)
        # dist = distance_transform_edt(image > T)
        # return contrast_stretching(dist)

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWTransform()
    ow.show()
    appl.exec_()
