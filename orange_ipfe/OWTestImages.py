"""
<name>Test Image</name>
<description>Select one on the standard images including: Camera, Checkerboard, COins, Lena, Moon, Scanned page or Text.</description>
<icon>icons/testimages.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>40</priority>
"""

import Orange  # needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.data import camera, checkerboard, coins, lena, moon, page, text
from data.images import noisy_square, noisy_blobs, noisy_circles, stinkbug, nuclei, random
from data.images import peppers, baboon, sign, microstructure, mri, cells, cross, misc
from data.images import city, city_depth, aerial, overlapping_circles


class OWTestImages(OWImgWidget):
    settingsList = ['image_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWTestImages, self).__init__(parent, signalManager)

        # Inpute/outputs
        self.outputs = [("Images", list)]

        # Settings
        self.data = None
        self.auto_apply = True
        self.settings_changed = False
        self.image_id = 0
        self.method = [("City Scene", city),
                       ("City Scene (depth)", city_depth),
                       ("Aerial Image", aerial),
                       ("Camera", camera),
                       ("Checkerboard", checkerboard),
                       ("Coins", coins),
                       ('Lena', lena),
                       ('Moon', moon),
                       ('MRI', mri),
                       ('Scanned Page', page),
                       ('Grey-level "txt" image', text),
                       ('Stinkbug', stinkbug),
                       ("Nuclei", nuclei),
                       ("Peppers", peppers),
                       ("Baboon", baboon), ("Sign", sign),
                       ('Square (synthetic)', noisy_square),
                       ("Circles (synthetic)", noisy_circles),
                       ("Overlapping Circles (synthetic)",
                        overlapping_circles),
                       ("Blobs (synthetic)", noisy_blobs),
                       ("Cells (synthetic)", cells),
                       ("Cross (synthetic)", cross),
                       ("Misc (synthetic)", misc),
                       ("Random (synthetic)", random),
                       ("Microblobs (synthetic)", microstructure)]
        self.loadSettings()

        # GUI
        # TODO:  Use info section to display copyright info on images!
        # box = OWGUI.widgetBox(self.controlArea, "Info")
        # self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        # self.infob = OWGUI.widgetLabel(box, '')
        # OWGUI.separator(self.controlArea)

        cbox = OWGUI.widgetBox(self.controlArea, "Standard Test Images")
        method_names = [x[0] for x in self.method]
        OWGUI.radioButtonsInBox(cbox, self, "image_id", method_names,
                                callback=[self.process_images, self.apply_if])  # , self.show_copy])

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, "settings_changed", self.apply)

        self.process_images()

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.settings_changed = False

    def process_images(self):
        method = self.method[self.image_id][1]
        self.images = [OrangeImage(method())]
        self.create_thumbnails()
        self.apply_if()
        self.resize(10, 10)
        self.adjustSize()

if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWTestImages()
    ow.show()
    appl.exec_()
