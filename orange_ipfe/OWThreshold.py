"""
<name>Threshold</name>
<description>Threshold an image using either Otsu or an adaptive algorithm</description>
<icon>icons/threshold.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange  # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage import img_as_float
from skimage.filter import threshold_otsu, threshold_adaptive


class OWThreshold(OWImgWidget):
    settingsList = ['method_id', 'adaptive', 'adaptive_mode',
                    'auto_apply', 'adaptive_block_size', 'adaptive_offset', 'threshold']

    def __init__(self, parent=None, signalManager=None):
        super(OWThreshold, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [("Images", list, self.processImages)]
        self.outputs = [("Images", list)]

        self.data = None
        self.images = None

        # Settings
        self.data = None
        self.method = [("Otsu", self.otsu),
                       ("Adaptive", self.adaptive),
                       ('Threshold', self.threshold),
                       ("Mean value", self.mean)]  # , ('Guassian mixture', self.gaussian)]
        self.method_id = 0  # method function

        # Adaptive
        self.adaptive_items = ['gaussian', 'mean', 'median']
        self.adaptive = 0
        self.adaptive_mode_items = ['reflect', 'constant', 'nearest', 'mirror']
        self.adaptive_mode = 0
        self.adaptive_block_size = 17
        self.adaptive_offset = 0

        # Threshold
        self.threshold = 112

        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface
        box = OWGUI.widgetBox(self.controlArea, 'Method')
        methodNames = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, "method_id", items=methodNames,
                       callback=[self.show_if, self.update_images, self.apply_if])

        # Adaptive
        self.adaptive_box = OWGUI.widgetBox(
            self.controlArea, 'Adaptive Options')
        OWGUI.comboBox(
            self.adaptive_box, self, "adaptive", items=self.adaptive_items,
            callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.adaptive_box, self, "adaptive_block_size",
                      "Block size:", 3, 30, 2, callback=[self.update_images, self.apply_if])
        OWGUI.hSlider(self.adaptive_box, self, "adaptive_offset",
                      "Offset:", 0, 20, 5, callback=[self.update_images, self.apply_if])
        self.mode_adaptive = OWGUI.comboBox(
            self.adaptive_box, self, "adaptive_mode", label="Array borders",
            items=self.adaptive_mode_items, callback=[self.show_if, self.update_images, self.apply_if])

        # Specify Value
        self.threshold_box = OWGUI.widgetBox(self.controlArea, 'Options')
        OWGUI.hSlider(self.threshold_box, self, "threshold",
                      "Threshold:", 0, 255, 1, callback=[self.update_images, self.apply_if])

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, "settings_changed", self.apply)

        OWGUI.rubber(self.controlArea)

        # Make sure GUI is consistent with settings
        self.show_if()

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.settings_changed = False

    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 1:  # Adaptive
            self.threshold_box.hide()
            self.null_option_box.hide()
            self.adaptive_box.show()
        elif self.method_id == 2:  # User
            self.adaptive_box.hide()
            self.null_option_box.hide()
            self.threshold_box.show()
        else:  # Otsu
            self.threshold_box.hide()
            self.adaptive_box.hide()
            self.option_seperator.hide()
            self.null_option_box.show()  # Makes widget behaviour consistent

    def processImages(self, images):
        self.data = images
        if images != None:
            function = self.method[self.method_id][1]
            self.images = [OrangeImage(function(
                image.gray().data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d images processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data != None:
            self.processImages(self.data)

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.
    def adaptive(self, image):
        return threshold_adaptive(image, block_size=self.adaptive_block_size,
                                  method=self.adaptive_items[
                                  self.adaptive], offset=self.adaptive_offset,
                                  mode=self.adaptive_mode_items[self.adaptive_mode])

    def otsu(self, image):
        image = img_as_float(image)
        return image > threshold_otsu(image)

    def threshold(self, image):
        image = img_as_float(image)
        threshold = float(self.threshold) / 255.0
        return image > threshold

    def mean(self, image):
        image = img_as_float(image)
        return image > image.mean()

if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWThreshold()
    ow.show()
    appl.exec_()
