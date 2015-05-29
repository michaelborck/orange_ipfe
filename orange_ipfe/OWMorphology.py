"""
<name>Morphology</name>
<description>Process images based on shapes by applying a structural element to
an input image and creating an output image f the same size. e.g. dilation,
erosion</description>
<icon>icons/morphology.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.morphology import closing, opening, erosion, dilation, square, diamond, rectangle, disk, skeletonize
from skimage.filters import canny
from skimage.color import rgb2gray


class OWMorphology(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWMorphology, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements
        self.method = [('Skeleton', self.skeletonize),
                       ('Opening', self.opening),
                       ('Closing', self.closing),
                       ('Erode', self.erosion),
                       ('Dilate', self.dilation)]

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

        # Opening/Closing/Erode/Dilate options
        self.neighbourhood_box = OWGUI.widgetBox(
            self.controlArea, 'Neighborhood Options')
        names = [x[0] for x in self.neighbourhood_names]
        OWGUI.radioButtonsInBox(
            self.neighbourhood_box, self, "neighbourhood_id", names,
            callback=[self.show_if, self.update_images, self.apply_if])  # , self.show_copy])
        OWGUI.hSlider(self.neighbourhood_box, self, "neighbourhood_size",
                      "Width/Radius:", 1, 10, 1, callback=[self.update_images, self.apply_if])
        self.spin = OWGUI.hSlider(
            self.neighbourhood_box, self, "neighbourhood_height",
            "Height:", 1, 10, 1, callback=[self.update_images, self.apply_if])

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
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
        if self.method_id == 0:
            self.option_seperator.hide()
            self.neighbourhood_box.hide()
            self.null_option_box.show()  # Makes widget behaviour consistent
        else:
            self.null_option_box.hide()
            self.neighbourhood_box.show()
            if self.neighbourhood_id == 2:
                self.spin.setEnabled(True)
            else:
                self.spin.setEnabled(False)

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
            self.images = [OrangeImage(method(
                image.gray().data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.
    def skeletonize(self, image):
        return skeletonize(canny(rgb2gray(image)))

    def opening(self, image):
        shape = self.neighbourhood_names[self.neighbourhood_id][1]
        if self.neighbourhood_id == 2:  # rectangle
            return opening(image, shape(self.neighbourhood_size, self.neighbourhood_height))
        else:
            return opening(image, shape(self.neighbourhood_size))

    def closing(self, image):
        shape = self.neighbourhood_names[self.neighbourhood_id][1]
        if self.neighbourhood_id == 2:  # rectangle
            return closing(image, shape(self.neighbourhood_size, self.neighbourhood_height))
        else:
            return closing(image, shape(self.neighbourhood_size))

    def erosion(self, image):
        shape = self.neighbourhood_names[self.neighbourhood_id][1]
        if self.neighbourhood_id == 2:  # rectangle
            return erosion(image, shape(self.neighbourhood_size, self.neighbourhood_height))
        else:
            return erosion(image, shape(self.neighbourhood_size))

    def dilation(self, image):
        shape = self.neighbourhood_names[self.neighbourhood_id][1]
        if self.neighbourhood_id == 2:  # rectangle
            return dilation(image, shape(self.neighbourhood_size, self.neighbourhood_height))
        else:
            return dilation(image, shape(self.neighbourhood_size))


if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWMorphology()
    ow.show()
    appl.exec_()
