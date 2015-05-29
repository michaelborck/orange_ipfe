"""
<name>Saliency</name>
<description>Create a salicency map. ALgorithms available include:
    Spectral Residual, Frequency Tunned</description>
<icon>icons/saliency.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange  # needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from ipfe.saliency import spectral_residual, frequency_tuned, edge_based, \
    luminance_and_colour, maximum_symmetric_surround, phase_map


class OWSaliency(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWSaliency, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [("Images", list, self.process_images)]
        self.outputs = [("Images", list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements.
        self.method = [("Spectral Residual", spectral_residual),
                       ("Frequency Tuned", frequency_tuned),
                       ("Edge based", edge_based),
                       ("FFT Phase", phase_map),
                       ("Luminance and Colour", luminance_and_colour),
                       ("Max. Symmetric Surround", maximum_symmetric_surround)]

        # Settings
        self.method_id = 0  # method function
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Options")
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, "method_id", items=method_names,
                       callback=[self.update_images, self.apply_if])

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, "settings_changed", self.apply)

        OWGUI.rubber(self.controlArea)

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
        if images is not None:
            method = self.method[self.method_id][1]
            self.images = [OrangeImage(method(image.data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d images processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data is not None:
            self.process_images(self.data)

if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWSaliency()
    ow.show()
    appl.exec_()
