"""
<name>Straighten</name>
<description>Finda the largest squear in image and adjust the perspective</description>
<icon>icons/straighten.png</icon>
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

from ipfe.perspective import find_squares, straighten_square


class OWStraighten(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWStraighten, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None


        # Methods this widget implements.
        self.method = [("Largest Square", self.largest_square),
                       ("Others...", self.soon)]

        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

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
            self.null_option_box.hide()
        else:
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

    # The following method performs any necessary pre/post-processing.
    def largest_square(self, data):
        squares = find_squares(data)
        if len(squares) > 0:
            M, maxWidth, maxheight, image = straighten_square(data, squares[0])
        else:
            image = data
        return image

    def soon(self, data):
        return camera()

    def array_to_table(self, image):
        # d = orange.Domain([orange.FloatVariable('a%i' % x) for x in range(5)])
        # a = Numeric.array([[1, 2, 3, 4, 5], [5, 4, 3, 2, 1]])
        return Orange.data.table(image)

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWStraighten()
    ow.show()
    appl.exec_()
