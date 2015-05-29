"""
<name>Kinect</name>
<description>Loads image(s) from a Kinect</description>
<icon>icons/kinect.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>10</priority>
"""

import Orange  # Needed to test outside orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage

from openni import *
import numpy as np
import time

ctx = Context()
ctx.init()
depth = DepthGenerator()
depth.create(ctx)
depth.set_resolution_preset(RES_VGA)
depth.fps = 30
ctx.start_generating_all()

class OWKinect(OWImgWidget):
    settingsList = [
        "load_grayscale", "show_preview", "auto_apply", "self_directory"]

    def __init__(self, parent=None, signalManager=None):
        super(OWKinect, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.outputs = [('Images', list)]

        # Settings
        self.load_grayscale = False
        self.show_preview = True
        self.settings_changed = False
        self.auto_apply = True
        self.directory = '/Users/michael/images/'
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data loaded.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        self.options_box = OWGUI.widgetBox(self.controlArea, "Load")
        #OWGUI.checkBox(self.options_box, self,
                       #'load_grayscale', 'Load as Grayscale')
        #OWGUI.checkBox(self.options_box, self, 'show_preview',
                       #'Show Thumbnails', callback=self.preview_if)
        OWGUI.button(self.options_box, self,
                     'Start Capture', callback=self.process_images)

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply")
        apply_button = OWGUI.button(box, self, "Apply", callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, "settings_changed", self.apply)

        OWGUI.rubber(self.controlArea)

        # Make sure GUI is consistent with settings
        self.preview_if()

    def process_images(self):
        self.images = []
        self.load_images()
        if self.images and self.show_preview:
            self.create_thumbnails()
        self.apply_if()

    def load_images(self):
        #filenames = OWGUI.QFileDialog.getOpenFileNames(self,
                          #caption='Select images...', directory=self.directory,
                          #filter="Image Files (*.png *.jpg *.bmp)")
        #self.images = [OrangeImage.load(fname) for fname in filenames]
        ## Filter images that were not loaded successfuly
        #self.images = filter(lambda img: img is not None, self.images)
        #if self.load_grayscale:
            #self.images = [OrangeImage((image.gray()).data)
                           #for image in self.images]
        #self.infoa.setText('%d image(s) loaded' % len(self.images))
        import cv2
        cv2.namedWindow("preview")
        while True:
            nRetVal = ctx.wait_one_update_all(depth)
            frame = np.fromstring(depth.get_raw_depth_map_8(), "uint8").reshape(480, 640)
            self.images =[OrangeImage(frame)]
            self.apply_if()
            cv2.imshow("preview",frame)
            key = cv2.waitKey(20)
            if key == 27:
                break
        cv2.destroyWindow("preview")

    def preview_if(self):
        self.mainArea.hide()
        #if self.show_preview:
            #self.mainArea.show()
        #else:
            #self.mainArea.hide()

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.settings_changed = False

if __name__ == '__main__':
    appl = OWGUI.QApplication([__file__])
    ow = OWKinect()
    ow.show()
    appl.exec_()
