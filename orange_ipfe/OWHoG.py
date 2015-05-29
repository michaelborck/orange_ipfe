"""
<name>HoG</name>
<description>Use various techniques to measure changes in gradients
for pixels, edges, or blocks. </description>
<icon>icons/hog.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.feature import hog
from skimage import exposure


class OWHoG(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWHoG, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [("Images", list, self.process_images)]
        self.outputs = [("Images", list),("Descriptor", Orange.data.Table)]

        # Instance Attributes
        self.data = None
        self.images = None

        # Methods this widget implements.
        self.method = [
            ("Histogram of Gradients", self.hog),
        ]

        # Settings
        self.method_id = 0  # method function
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        # Attributes for methods that have settings/options
        # HoG attributes
        self.hog_cell_width = 16
        self.hog_cell_height = 16
        self.hog_orientations = 8
        self.hog_block_width = 1
        self.hog_block_height = 1

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Options")
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, "method_id", items=method_names,
                       callback=[self.show_if, self.update_images, self.apply_if])

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface
        # HoG GUI
        self.hog_box = OWGUI.widgetBox(self.controlArea, "Cell Size (Pixels)")
        OWGUI.hSlider(
            self.hog_box, self, "hog_orientations", label='Orientations: ',
            minValue=1, maxValue=8, step=1)
        OWGUI.hSlider(
            self.hog_box, self, "hog_cell_width", label='Cell Width: ',
            minValue=1, maxValue=40, step=1)
        OWGUI.hSlider(
            self.hog_box, self, "hog_cell_height", label='Cell Height: ',
            minValue=1, maxValue=40, step=1)
        OWGUI.hSlider(
            self.hog_box, self, "hog_block_width", label='Block Width: ',
            minValue=1, maxValue=9, step=1)
        OWGUI.hSlider(
            self.hog_box, self, "hog_block_height", label='Block Height: ',
            minValue=1, maxValue=9, step=1)
        OWGUI.button(
            self.hog_box, self, "Update Images", callback=self.update_images)

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback=self.apply)
        auto_apply_cb = OWGUI.checkBox(
            box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(
            self, apply_button, auto_apply_cb, "settings_changed", self.apply)

        OWGUI.rubber(self.controlArea)

        self.show_if()

    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 0:  # HoG
            self.null_option_box.hide()  # Makes widget behaviour consistent
            self.hog_box.show()
        else:
            self.hog_box.hide()
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
            self.images = [OrangeImage(method((
                image.gray()).data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post processing.
    def soon(self, data):
        return data

    def hog(self, image):
        descriptor, hog_image = hog(image, orientations=self.hog_orientations,
                                    pixels_per_cell=(
                                        self.hog_cell_width, self.hog_cell_height),
                                    cells_per_block=(
                                        self.hog_block_width, self.hog_block_height),
                                    visualise=True)
        # Rescale histogram for better display
        return exposure.rescale_intensity(hog_image, in_range=(0, 0.02))

if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWGradient()
    ow.show()
    appl.exec_()
