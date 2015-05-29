"""
<name>Segment</name>
<description>Segment an image using either Quickshift, SLIC, or Felzenszwab (Graph Based) algorithm</description>
<icon>icons/segment.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
#from skimage.segmentation import quickshift, slic, felzenszwalb, visualize_boundaries #mark_boundaries in 0.8
from skimage.segmentation import quickshift, slic, felzenszwalb, mark_boundaries #mark_boundaries in 0.8
from skimage import img_as_float
import numpy as np
from pymorph import cwatershed
# from mahotas import gvoronoi
from mahotas.segmentation import gvoronoi
from skimage.morphology import watershed #, is_local_maximum
from skimage.filters import threshold_otsu, threshold_adaptive
from scipy import ndimage
from skimage import img_as_ubyte
import mahotas
import pymorph

#from ipamv.transform import distance
#from ipfe.morphology import labels
#from ipamv.exposure import contrast_stretch

class OWSegment(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']
    def __init__(self, parent=None, signalManager=None):
        super(OWSegment, self).__init__(parent, signalManager)

        self.inputs = [("Images", list, self.process_images)]
        self.outputs = [("Images", list)]
        self.method = [("Quickshift", self.quickshift),
                       ("K-Means (slic)", self.slic),
                       ("Graph Based (felzenszwalb)", self.graph),
                       ("Watershed", self.watershed)
                       ]
        self.method_id = 0 # method function
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()

        self.data = None
        self.images = None
        self.seeds = None

        # Setting for methods
        # Graph Based
        self.graph_scale = 100
        self.graph_sigma = 0.5
        self.graph_min_size = 40

        # K-means
        self.kmeans_n_segments = 250
        self.kmeans_ratio = 10
        self.kmeans_sigma = 1
        self.convert2lab = True

        # Quickshift
        self.quick_kernel_size = 3
        self.quick_max_dist = 6
        self.quick_ratio = 0.5

        # All methods
        self.mark_boundaries = True

        # Watershed
        self.water_extend_to_plane = True
        self.water_remove_border = True
        self.water_sigma = 16

        # GUI
        box = OWGUI.widgetBox(self.controlArea, "Info")
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')


        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Method')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                callback=[self.show_if, self.update_images, self.apply_if])

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')


        # For each method that needs options/setting setup interface
        # Graph Based
        self.graph_box = OWGUI.widgetBox(self.controlArea, '')
        OWGUI.hSlider(self.graph_box, self, "graph_scale",
                "Scale (higher means larger cluster)", 10, 500, 50, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.graph_box, self, "graph_sigma",
                "Width of Gaussian Kernel", 0, 1, 0.1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.graph_box, self, "graph_min_size",
                "Minimum size", 10, 50, 1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.checkBox(self.graph_box, self, "mark_boundaries", "Overloay boundries?")

        # K-means Based
        self.kmeans_box = OWGUI.widgetBox(self.controlArea, '')
        OWGUI.hSlider(self.kmeans_box, self, "kmeans_n_segments",
                "Number of segments", 10, 5000, 50, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.kmeans_box, self, "kmeans_ratio",
                "Ratio", 1, 10, 1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.kmeans_box, self, "kmeans_sigma",
                "Sigma", 5, 30, 1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.checkBox(self.kmeans_box, self, "mark_boundaries", "Overloay boundries?",
                callback=[self.update_images, self.apply_if])

        # Quickshift
        self.quick_box = OWGUI.widgetBox(self.controlArea, '')
        OWGUI.hSlider(self.quick_box, self, "quick_kernel_size",
                "Kernel size", 3, 20, 1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.quick_box, self, "quick_max_dist",
                "Distance", 3, 20, 1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.hSlider(self.quick_box, self, "quick_ratio",
                "Ratio", 0, 1, 0.1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.checkBox(self.quick_box, self, "mark_boundaries", "Overloay boundries?",
                callback=[self.update_images, self.apply_if])

        # Watersheed
        self.water_box = OWGUI.widgetBox(self.controlArea, '')
        OWGUI.hSlider(self.water_box, self, "water_sigma",
                "Sigma", 5, 30, 1, callback=[self.show_if, self.update_images, self.apply_if])
        OWGUI.checkBox(self.water_box, self, "water_extend_to_plane", "Extend to whole plane",
                callback=[self.show_if, self.update_images, self.apply_if])
        self.rcob = OWGUI.checkBox(self.water_box, self, "water_remove_border", "Remove cells on border",
                callback=[self.update_images, self.apply_if])

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, "Apply Changes")
        apply_button = OWGUI.button(box, self, "Apply", callback = self.apply)
        auto_apply_cb = OWGUI.checkBox(box, self, "auto_apply", "Apply changes automatically")
        OWGUI.setStopper(self, apply_button, auto_apply_cb, "settingsChanged", self.apply)

        OWGUI.rubber(self.controlArea)
        self.show_if()

    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 0: # Quickshift
            self.null_option_box.hide()
            self.graph_box.hide()
            self.kmeans_box.hide()
            self.water_box.hide()
            self.quick_box.show()
        elif self.method_id == 1: # K-means (slic)
            self.null_option_box.hide()
            self.graph_box.hide()
            self.quick_box.hide()
            self.water_box.hide()
            self.kmeans_box.show()
        elif self.method_id == 2: # Graph Based (felzenszwalb)
            self.null_option_box.hide()
            self.quick_box.hide()
            self.kmeans_box.hide()
            self.water_box.hide()
            self.graph_box.show()
        elif self.method_id == 3: # Watershed
            self.null_option_box.hide()
            self.quick_box.hide()
            self.kmeans_box.hide()
            self.graph_box.hide()
            self.water_box.show()
            if self.water_extend_to_plane:
                self.rcob.setEnabled(True)
            else:
                self.rcob.setEnabled(False)
        else:
            self.option_seperator.hide()
            self.null_option_box.show() # Makes widget behaviour consistent

    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        self.send('Images', self.images)
        self.settingsChanged = False

    def process_images(self, images):
        self.data = images
        if images != None:
            method = self.method[self.method_id][1]
            self.images = [OrangeImage(method(image)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d images processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)

    def process_seeds(self, seeds):
        self.seeds = seeds
        if self.seeds:
            self.update_images()

    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.

    def quickshift(self, img):
        if img.is_gray():
            img = img.rgb()
        img = img_as_float(img.data[::2, ::2])
        segments =  quickshift(img, kernel_size=self.quick_kernel_size,
                max_dist=self.quick_max_dist, ratio=self.quick_ratio)
        self.infob.setText("Quickshift number of segments: %d" % len(np.unique(segments)))
        return self.visualize(img, segments)

    def slic(self, img):
        if img.is_gray():
            img = img.rgb()
        img = img_as_float(img.data[::2, ::2])
        segments =  slic(img, n_segments=self.kmeans_n_segments,
                compactness=self.kmeans_ratio, sigma=self.kmeans_sigma)
        self.infob.setText("K-means number of segments: %d" % len(np.unique(segments)))
        return self.visualize(img, segments)

    def graph(self, img):
        if img.is_gray():
            img = img.rgb()
        img = img_as_float(img.data[::2, ::2])
        segments = felzenszwalb(img, scale=self.graph_scale, sigma=self.graph_sigma,
                min_size=self.graph_min_size)
        self.infob.setText("Graph based number of segments: %d" % len(np.unique(segments)))
        return self.visualize(img, segments)

    def visualize(self, image, segments):
        if self.mark_boundaries:
            #return visualize_boundaries(image, segments)
            return mark_boundaries(image, segments)
        else:
            return segments

    def watershed(self, image):
        image = image.data
        seeds, nr_seeds = labels(image, self.water_sigma)
        dist = contrast_stretch(distance(image))
        segments = pymorph.cwatershed(dist, seeds)
        if self.water_extend_to_plane:
            whole = gvoronoi(segments)
        if self.water_extend_to_plane and self.water_remove_border:
            borders = np.zeros(segments.shape, np.bool)
            borders[ 0,:] = 1
            borders[-1,:] = 1
            borders[:, 0] = 1
            borders[:, -1] = 1
            at_border = np.unique(segments[borders])
            for obj in at_border:
                whole[whole == obj] = 0
        if self.water_extend_to_plane:
            return whole
        else:
            return segments

if __name__ == "__main__":
    appl = OWGUI.QApplication([__name__])
    ow = OWSegment()
    ow.show()
    appl.exec_()
