"""
<name>Image Operations</name>
<description>Basic image operations, finding the differance between two image, find the average of images</description>
<icon>icons/imageoperations.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange # Needed to test outside of Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from skimage.exposure import equalize_hist
import numpy as np
from pymorph import regmax, regmin, overlay
from scipy.ndimage import label
from skimage import img_as_ubyte
import matplotlib.pyplot as plt
from misc.matplotlib_tools import figAsArray


class OWImageOperations(OWImgWidget):
    settingsList = ['method_id', 'auto_apply']
    def __init__(self, parent=None, signalManager=None):
        super(OWImageOperations, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Images', list)]

        # Instance attributes
        self.data = None
        self.images = None

        # Methods this widget implements
        self.method = [('Average', self.average),
                       ('Histogram', self.histogram),
                       ('Region Max', self.region_max),
                       ('Region Min', self.region_min),
                       ('Label/Seeds', self.label)]

        # Settings attributes
        self.method_id = 0
        self.auto_apply = True
        self.settings_changed = False
        self.loadSettings()


        # Methods Attributes
        # Histogram
        self.include_image = False
        self.show_red = True
        self.show_green = True
        self.show_blue = True
        self.show_gray = True
        # Use Matplotlib plot window.  Need to keep track of if it is opened
        # When source changes, if plotted then need to cloe window fo rnew plot
        self.have_plot = False

        # Region Max/Min
        self.overlay = True

        # GUI
        box = OWGUI.widgetBox(self.controlArea, 'Info')
        self.infoa = OWGUI.widgetLabel(box, 'No data on input.')
        self.infob = OWGUI.widgetLabel(box, '')

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Options')
        method_names = [x[0] for x in self.method]
        OWGUI.comboBox(box, self, 'method_id', items=method_names,
                callback=[self.update_images, self.show_if])

        self.option_seperator = OWGUI.separator(self.controlArea)

        # This is the default "box" so widget resizing works
        # consistently for methods that have no options/settings.
        # Probably a better way to do this.
        self.null_option_box = OWGUI.widgetBox(self.controlArea, '')

        # For each method that needs options/setting setup interface

        # Histogram
        self.histogram_box = OWGUI.widgetBox(self.controlArea, 'Histogram Options')
        OWGUI.checkBox(self.histogram_box, self, 'include_image',
                'Include image:', callback=self.update_images)
        self.red_cb = OWGUI.checkBox(self.histogram_box, self, 'show_red',
                'Show Red channel:', callback=self.update_images)
        self.green_cb = OWGUI.checkBox(self.histogram_box, self, 'show_green',
                'Show Green channel:', callback=self.update_images)
        self.blue_cb = OWGUI.checkBox(self.histogram_box, self, 'show_blue',
                'Show Blue channel:', callback=self.update_images)
        self.gray_cb = OWGUI.checkBox(self.histogram_box, self, 'show_gray',
                'Show Grayscale:', callback=self.update_images)

        # Region Min/Max
        self.regminmax_box = OWGUI.widgetBox(self.controlArea, 'Histogram Options')
        self.overlay_cb = OWGUI.checkBox(self.regminmax_box, self, 'overlay',
                'Overlay:', callback=self.update_images)

        OWGUI.separator(self.controlArea)

        box = OWGUI.widgetBox(self.controlArea, 'Apply Changes')
        apply_button = OWGUI.button(box, self, 'Apply', callback = self.apply)
        auto_apply_cb = OWGUI.checkBox(box, self, 'auto_apply', 'Apply changes automatically')
        OWGUI.setStopper(self, apply_button, auto_apply_cb, 'settings_changed', self.apply)

        OWGUI.rubber(self.controlArea)
        # Make sure GUI is consistent with settings
        self.show_if()


    def show_if(self):
        # Assume we have options to show.
        self.option_seperator.show()
        if self.method_id == 1: # histogram
            self.null_option_box.hide()
            self.regminmax_box.hide()
            self.histogram_box.show()
        elif 2 <= self.method_id <= 3: # Region Min/Max
            self.null_option_box.hide()
            self.histogram_box.hide()
            self.regminmax_box.show()
        else:
            self.regminmax_box.hide()
            self.histogram_box.hide()
            self.option_seperator.hide()
            self.null_option_box.show() # Makes widget behaviour consistent

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
            if self.method_id == 0: # Average
                self.images = []
                self.images.append(OrangeImage(self.average(images)))
            else:
                method = self.method[self.method_id][1]
                self.images = [OrangeImage(method(image.data)) for image in images]
            self.create_thumbnails()
            self.infoa.setText('%d image(s) processed' % len(self.images))
            self.apply_if()

    def update_images(self):
        if self.data:
            self.process_images(self.data)


    # The following methods are simple wrappers around various Python modules
    # Allows us to perform any necessary pre/post-processing.

    def average(self, images):
        all_images = np.copy(images[0].data)
        for image in images[1:]:
            all_images += image.data
        average = all_images / len(images)
        return average

    def histogram(self, image):
        def plot_histogram(num_bins=60):
            if image.ndim == 3:
                self.red_cb.setEnabled(True)
                self.green_cb.setEnabled(True)
                self.blue_cb.setEnabled(True)
                if self.show_red:
                    hist, bin_edges = np.histogram(image[:,:, 0], bins=num_bins)
                    bins = 0.5*(bin_edges[:-1] + bin_edges[1:])
                    plt.plot(bins, hist, color='r', lw=3)
                if self.show_green:
                    hist, bin_edges = np.histogram(image[:,:, 1], bins=num_bins)
                    bins = 0.5*(bin_edges[:-1] + bin_edges[1:])
                    plt.plot(bins, hist, color='g', lw=3)
                if self.show_blue:
                    hist, bin_edges = np.histogram(image[:,:, 2], bins=num_bins)
                    bins = 0.5*(bin_edges[:-1] + bin_edges[1:])
                    plt.plot(bins, hist, color='b', lw=3)
                # Grayscale
                # im = image.mean(axis=2)  # Almost the same as formula below
                img = image[:,:, 0] * 0.299 + image[:,:, 1] * 0.587 + image[:,:, 2] * 0.114
            else:
                self.red_cb.setEnabled(False)
                self.green_cb.setEnabled(False)
                self.blue_cb.setEnabled(False)
                img = image

            if self.show_gray:
                hist, bin_edges = np.histogram(img, bins=num_bins)
                bins = 0.5*(bin_edges[:-1] + bin_edges[1:])
                plt.plot(bins, hist, color='gray', lw=3)

        if self.have_plot:
            plt.close()
            self.have_plot = False

        self.have_plot = True
        if self.include_image:
            fig = plt.figure(figsize=(11, 4))
            plt.subplot(121)
            plt.imshow(image, cmap=plt.cm.gray)
            plt.axis('off')
            plt.subplot(122)
            plot_histogram()
            im = figAsArray(fig)
        else:
            fig = plt.figure(figsize=(5, 4))
            plot_histogram()
            im = figAsArray(fig)
        return im

    def region_max(self, image):
        # regmax can't handle float64
        img = img_as_ubyte(image)
        rmax = regmax(img)
        if self.overlay:
            return overlay(img, rmax)
        else:
            return rmax

    def region_min(self, image):
        # regmin can't handle float64
        img = img_as_ubyte(image)
        rmin = regmin(img)
        if self.overlay:
            return overlay(img, rmin)
        else:
            return rmin

    def label(self, image):
        seeds, nr_seeds = label(image)
        self.infob.setText('%d regions in last image processed' % nr_seeds)
        return seeds

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWImageOperations()
    ow.show()
    appl.exec_()
