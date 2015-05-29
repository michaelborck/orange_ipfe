"""
<name>Edges</name>
<description>Use edge detectors such as Canny to detect edges in an image</description>
<icon>icons/edges.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget

import numpy as np
from scipy.ndimage import convolve
from OrangeImage import OrangeImage
from skimage import img_as_float
from skimage.feature import canny
from ipfe.masks import sobel_masks, prewitt_masks, kirsch_masks, robinson_masks, scharr_masks
from skimage.transform import probabilistic_hough_line
from skimage.draw import line

class OWEdges(OWImgWidget):
    settingsList = ['method_id', 'auto_apply', 'angle']
    def __init__(self, parent=None, signalManager=None):
        super(OWEdges, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [("Images", list, self.process_images)]
        self.outputs = [("Images", list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements.
        self.method = [("Canny", self.canny),
                       ("Sobel", self.edges),
                       ("Prewitt", self.edges),
                       ("Kirsch",  self.edges),
                       ("Roberts", self.edges),
                       ("Scharra", self.edges),
                       ("Hough", self.hough_lines)]

        # Settings
        self.method_id = 0 # method function
        self.auto_apply = True
        self.angle = 0
        self.settings_changed = False
        self.loadSettings()

        # Hough Settings
        self.hough_threshold = 10
        self.hough_length = 5
        self.hough_gap = 3

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        # Setup interface for various methods this widget implements
        box = OWGUI.widgetBox(self.controlArea, 'Options')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                callback=[self.show_if, self.update_images])

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')


        # For each method that needs options/setting setup interface
        # Sobel, Prewitt, Kirsch, Robinson, Scharra
        self.mask_box = OWGUI.widgetBox(self.controlArea, "Orientation")
        self.rbbox = OWGUI.radioButtonsInBox(self.mask_box, self, "angle", [],
                 callback = [self.update_images, self.apply_if])
        # Need to store individual buttons so easy to enable/disable
        # TODO: Now hide/show boxes no need to append radio buttons
        self.rbc0 = OWGUI.appendRadioButton(self.rbbox, self, "angle", "Edge Map")
        self.rbc1 = OWGUI.appendRadioButton(self.rbbox, self, "angle", "Vertical")
        self.rbc2 = OWGUI.appendRadioButton(self.rbbox, self, "angle", "Positive Diagonal (45/225)")
        self.rbc3 = OWGUI.appendRadioButton(self.rbbox, self, "angle", "Horiziontal")
        self.rbc4 = OWGUI.appendRadioButton(self.rbbox, self, "angle", "Negative Diagonal (135/415)")

        self.hough_box = OWGUI.widgetBox(self.controlArea, "Hough Lines")
        OWGUI.hSlider(self.hough_box, self, "hough_threshold", "Threshold:", 1,
                20, 1, callback=self.update_images)
        OWGUI.hSlider(self.hough_box, self, "hough_length", "Line Length:", 1,
                20, 1, callback=self.update_images)
        OWGUI.hSlider(self.hough_box, self, "hough_gap", "Line Gap:", 1,
                10, 1, callback=self.update_images)

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback = self.apply)
        auto_apply_cb = OWGUI.checkBox(box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(self, apply_button, auto_apply_cb, "settings_changed", self.apply)

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

    def process_images(self, images):
        self.data = images
        if images != None:
            method = self.method[self.method_id][1]
            self.images = [OrangeImage(method(image.gray().data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d images processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data != None:
            self.process_images(self.data)

    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 0: # Canny
            self.mask_box.hide()
            self.hough_box.hide()
            self.option_seperator.hide()
            self.null_option_box.show() # Makes widget behaviour consistent
        elif self.method_id == 6: # Hough lines
            self.mask_box.hide()
            self.null_option_box.hide()
            self.hough_box.show()
        else:
            self.null_option_box.hide()
            self.hough_box.hide()
            self.mask_box.show()

    # The following method performs any necessary pre/post-processing.
    def canny(self, image):
        return canny(image)

    # TODO: Move into a library module
    def edges(self, image):
        def edge_filter(image, mask):
            image = img_as_float(image)
            result = np.abs(convolve(image, mask))
            result[0,:] = 0
            result[-1,:] = 0
            result[:, 0] = 0
            result[:, -1] = 0
            return result

        def edge_map(image, masks):
            return np.sqrt(edge_filter(image, masks[0])**2 +
                    edge_filter(image, masks[2])**2)

        # TODO:  Fix, this! Sure I can do something clever with dicts!
        if self.method_id == 1:
            if self.angle == 0: # Sobel Edge Map
                return edge_map(image, sobel_masks)
            else:
                return edge_filter(image, sobel_masks[self.angle-1])
        elif self.method_id == 2:
            if self.angle == 0: # Prewitt Edge Map
                return edge_map(image, prewitt_masks)
            else:
                return edge_filter(image, prewitt_masks[self.angle-1])
        elif self.method_id == 3:
            if self.angle == 0: # Kirsch Edge Map
                return edge_map(image, kirsch_masks)
            else:
                return edge_filter(image, kirsch_masks[self.angle-1])
        elif self.method_id == 4:
            if self.angle == 0: # Robinson Edge Map
                return edge_map(image, robinson_masks)
            else:
                return edge_filter(image, robinson_masks[self.angle-1])
        elif self.method_id == 5:
            if self.angle == 0: # Scharr Edge Map
                return edge_map(image, scharr_masks)
            else:
                return edge_filter(image, scharr_masks[self.angle-1])


    def hough_lines(self, image):
        edges = canny(image)
        # edges = image  # Assume user provides a edge map!
        lines = probabilistic_hough_line(edges, threshold=self.hough_threshold,
                line_length=self.hough_length, line_gap=self.hough_gap)
        edges = edges * 0
        for aline in lines:
            p0, p1 = aline
            # rr, cc = bresenham(p0[0],p0[1], p1[0],p1[1])
            rr, cc = line(p0[0], p0[1], p1[0], p1[1])
            edges[cc, rr] += 1
        return edges


if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWEdges()
    ow.show()
    appl.exec_()
