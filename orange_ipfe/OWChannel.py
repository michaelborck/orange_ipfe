"""
<name>Channel</name>
<description>Select one of the channels available in the image.</description>
<icon>icons/channel.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage


class OWChannel(OWImgWidget):
    settings = ["channel", "auto_apply"]

    def __init__(self, parent=None, signalManager=None):
        super(OWChannel, self).__init__(parent, signalManager)

        self.inputs = [("Images", list, self.process_images)]
        self.outputs = [("Images", list)]
        self.channel = 0
        self.data = None
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)
        cbox = OWGUI.widgetBox(self.controlArea, "Channel Select")
        rbbox = OWGUI.radioButtonsInBox(cbox, self, "channel", [],
                                        callback=[self.update_images, self.apply_if])
        self.rbc0 = OWGUI.appendRadioButton(
            rbbox, self, "channel", "R|H|L|C|X Channel 1")
        self.rbc1 = OWGUI.appendRadioButton(
            rbbox, self, "channel", "G|S|a|i|Y Channel 2")
        self.rbc2 = OWGUI.appendRadioButton(
            rbbox, self, "channel", "B|V|b|e|Z Channel 3")
        self.rbc3 = OWGUI.appendRadioButton(
            rbbox, self, "channel", "Alpha Channel 4")

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
        self.selection()
        if images != None:
            if not images[0].is_gray():
                self.images = [OrangeImage((image.data[
                                           :, :, self.channel])) for image in images]
            else:
                self.images = images
            self.create_thumbnails()
            self.infoa.setText('%d images processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    def selection(self):
        if self.data:
            if self.data[0].is_gray():
                self.channel = 0
                self.rbc1.setEnabled(False)
                self.rbc2.setEnabled(False)
                self.rbc3.setEnabled(False)
            else:
                self.rbc1.setEnabled(True)
                self.rbc2.setEnabled(True)
                self.rbc3.setEnabled(True)
                if not self.data[0].has_alpha():
                    self.rbc3.setEnabled(False)


if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWChannel()
    ow.show()
    appl.exec_()
