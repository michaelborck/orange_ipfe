"""
<name>Colour space</name>
<description>Convert inputs to RGB, HSV, LAB, CIE, XYZ, or Gray colour space.
Conversion occurs through the central RGB colour space, i.e. conversion from
XYZ to HSV is implemented as XYZ -> RGB -> HSV instead of directly.</description>
<icon>icons/colourspace.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from ImgWidget import OWImgWidget


class OWColourspace(OWImgWidget):
    settingsList = ['to_space', 'auto_Apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWColourspace, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [("Images", list, self.process_images)]
        self.outputs = [("Images", list)]

        # Settings
        self.to_space = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        cbox = OWGUI.widgetBox(self.controlArea, "Convert Colour Space")
        rbbox = OWGUI.radioButtonsInBox(cbox, self, "to_space", [],
                                        callback=[self.update_images, self.apply_if])
        self.rbc0 = OWGUI.appendRadioButton(rbbox, self, "to_space", "RGB")
        self.rbc1 = OWGUI.appendRadioButton(rbbox, self, "to_space", "HSV")
        self.rbc2 = OWGUI.appendRadioButton(rbbox, self, "to_space", "LAB")
        self.rbc3 = OWGUI.appendRadioButton(rbbox, self, "to_space", "CIE")
        self.rbc4 = OWGUI.appendRadioButton(rbbox, self, "to_space", "XYZ")
        self.rbc5 = OWGUI.appendRadioButton(
            rbbox, self, "to_space", "Grayscale")

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, "settings_changed", self.apply)

        OWGUI.rubber(self.controlArea)
        self.adjustSize()

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
            self.images = [self.to_colour_space(image) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d images processed' % len(self.images))

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    def to_colour_space(self, img):
        return {0: img.rgb(),
                1: img.hsv(),
                2: img.lab(),
                3: img.cie(),
                4: img.xyz(),
                5: img.gray()}[self.to_space]

if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWColourspace()
    ow.show()
    appl.exec_()
