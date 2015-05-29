"""
<name>Local Depth Pattern</name>
<description>Local Depth Pattern
<icon>icons/ldp.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from OWWidget import *
from ipamv.features.depth import local_depth_pattern


class OWLDP(OWWidget):
    settingsList = ['auto_apply', 'block_size']

    def __init__(self, parent=None, signalManager=None):
        super(OWLDP, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Data', ExampleTable)]

        # Attributes
        self.data = None
        self.images = None

        # Settings attributes
        self.auto_apply = True
        self.settings_changed = False
        self.label = "UNK"
        self.loadSettings()
        self.block_size = 8

        # Methods Attributes

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        OWGUI.hSlider(self.controlArea, self, "block_size",
                      "Block size:", 3, 30, 2, callback=[self.update_description, self.apply_if])
        box = OWGUI.widgetBox(self.controlArea, "Label Class")
        OWGUI.lineEdit(box, self, "label", label="Class:",
                       orientation="horizontal", labelWidth=40,
                       callback=self.update_description)

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Apply Changes')
        apply_button = OWGUI.button(box, self, 'Apply', callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, 'auto_apply', 'Apply changes automatically')
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, 'settings_changed', self.apply)

        # OWGUI.rubber(self.controlArea)
        self.update_description()

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Data', self.data)
        self.settings_changed = False

    def process_images(self, images):
        self.images = images
        self.update_description()

    def update_description(self):
        if self.images != None:
            feature_vector = [self.describe(
                image.data) for image in self.images]
            print feature_vector[0]
            descriptors_and_status = [Orange.feature.Descriptor.make('ldp%i' % x, Orange.feature.Type.Continuous)
                                      for x in range(len(feature_vector[0]) - 1)]
            # Get rid of status codes from the 'make' calls.
            descriptors = [pair[0] for pair in descriptors_and_status]
            # Reuse the 'Label' descriptor
            descriptors.append(Orange.feature.Descriptor.make(
                'Label', Orange.feature.Type.Discrete, ["UNK", "BS", "TL"])[0])
            domain = Orange.data.Domain(descriptors)
            self.data = Orange.data.Table(domain, feature_vector)
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def describe(self, image):
        ldp = local_depth_pattern(image, self.block_size).tolist()
        ldp.append(str(self.label))
        return ldp

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWLDP()
    ow.show()
    appl.exec_()
