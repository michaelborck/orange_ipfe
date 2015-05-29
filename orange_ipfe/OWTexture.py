"""
<name>Texture</name>
<description>Create a </description>
<icon>icons/texture.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from data.images import sign

from mahotas.features import haralick


class OWTexture(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWTexture, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements
        self.method = [('Method 1', self.soon), ('Method 2', self.soon)]

        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # Methods Attributes

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
    def soon(self, data):
        return sign()


if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWTexture()
    ow.show()
    appl.exec_()
