"""
<name>Interest Points</name>
<description>Extract interesting point from an image. e.g. corners </description>
<icon>icons/interestpoints.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange  # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
import numpy as np
from skimage import img_as_float, color
from pylab import *

#from ipfe.data import sign
from ipfe.imagery import patch_Harris

class OWInterestPoints(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWInterestPoints, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements
        self.method = [('Harris', self.harris), ('SIFT', self.soon),
                       ('SURF', self.soon), ('FAST', self.soon)]

        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # Methods Attributes
        self.harris_maps = ['Response Map', 'Points Mask', 'Overlay']
        self.harris_map_id = 2
        self.harris_distance = 5
        self.harris_sigma = 3
        self.harris_threshold = 0.1

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface
        box = OWGUI.widgetBox(self.controlArea, 'Options')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                       callback=[self.show_if, self.update_images])

        self.harris_box = OWGUI.widgetBox(self.controlArea, 'Harris Option')
        OWGUI.hSlider(self.harris_box, self, "harris_distance", "Distance:", 1,
                      10, 1, callback=self.update_images)
        # OWGUI.spin(self.harris_box, self, 'harris_threshold', min=0.1, max=1,step=0.1,
                # label='Threshold:', callback=[self.update_images,
                # self.apply_if])
        OWGUI.hSlider(self.harris_box, self, "harris_sigma", "Sigma:", 1,
                      10, 1, callback=self.update_images)
        OWGUI.radioButtonsInBox(
            self.harris_box, self, "harris_map_id", self.harris_maps,
            callback=[self.show_if, self.update_images, self.apply_if])  # , self.show_copy])

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
        if self.method_id == 0:  # Harris
            self.harris_box.show()
            self.null_option_box.hide()
        else:
            self.harris_box.hide()
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
    def soon(self, image):
        return image

    def harris(self, img):
        image = np.array(img, copy=True)
        # if len(image.shape) > 2:
            # image = color.rgb2gray(image)
        harris_response = harris.compute_response(
            image, sigma=self.harris_sigma)
        filtered_coords = harris.get_points(harris_response,
                                            min_dist=self.harris_distance, threshold=self.harris_threshold)
        if self.harris_map_id == 0:  # response map
            return harris_response
        elif self.harris_map_id == 1:  # Point mask
            img = zeros(img.shape)
        return harris.overlay_points(img, filtered_coords)


if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWInterestPoints()
    ow.show()
    appl.exec_()
