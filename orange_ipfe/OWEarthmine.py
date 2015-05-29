"""
<name>Earthmine</name>
<description>Connect, navigate a Earthmine server</description>
<icon>icons/ea.png</icon>
<priority>10</priority>
"""

import Orange
import OWGUI
from ImgWidget import OWImgWidget
from OrangeImage import OrangeImage
from PyQt4 import QtCore, QtGui
import urllib
from skimage import io
from scipy import misc

from subprocess import call
import os
from misc.imtools import url_to_img
from data.earthmine import EarthmineView
from data.earthmine_index import PanoInfo

import sys
import os
import math
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class OWEarthmine(OWImgWidget):
    settingsList = ['server', 'key', 'secret', 'img_width', 'service',
                    'tile', 'coverage', 'img_height', 'fov', 'sr', 'mr',
                    'dot', 'fqi', 'auto_apply']

    def __init__(self, parent=None, signalManager=None):
        super(OWEarthmine, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.outputs = [('Images', list)]

        # Attributes
        self.data = None
        self.images = None

        # Settings attributes
        self.auto_apply = True
        self.settings_changed = False
        self.img_width = 1024
        self.img_height = 1024
        self.fov = 90
        self.sr = 80
        self.mr = 1
        self.dot = False
        self.fqi = False
        self.lat = ""
        self.lon = ""
        self.lat_lon_add = 0
        #self.service = "http://service.earthmineaustralia.com/service"
        #self.tile = "http://tile.earthmineaustralia.com/www"
        #self.coverage = "http://service.earthmineaustralia.com/map/"
        #self.server="service.earthmineaustralia.com"
        #self.key = "8mft3ewybww03ln1ck3wqjas"
        #self.secret = "ra1H3qwXHT"
        self.service = "http://localhost:11114/service"
        self.tile = "http://localhost:11114/www"
        self.coverage = "http://localhost:11114/map/"
        self.server="localhost:11114"
        self.key = "nzfmfh816c820hd247x0clzd"
        self.secret = "PKgtGNTdYf"
        self.loadSettings()

        self.listLabels = []
        self.listValues = [0]

        self.traffic_light = 0
        self.parking_meter = 0
        self.traffic_sign = 0
        self.street_sign = 0
        self.rubbish_bins = 0

        self.lat_lon = 0
        self.from_file = 0
        self.view = EarthmineView(server=self.server, key=self.key, secret=self.secret)

        self.panos = PanoInfo()
        self.panos["name"] = "/Users/michael/EA_INDX.csv"
        # Methods Attributes
        # GUI
        self.tabs = OWGUI.tabWidget(self.controlArea)

        tab = OWGUI.createTabPage(self.tabs, "Navigate")
        box = OWGUI.widgetBox(tab, '')

        rbbox = OWGUI.radioButtonsInBox(tab, self, "lat_lon_add", [],
                                        callback=[self.update_images, self.apply_if])
        self.rbc0 = OWGUI.appendRadioButton( rbbox, self, "street_sign", "Street Sign")
        self.rbc0 = OWGUI.appendRadioButton( rbbox, self, "parking_meter", "Parking Meter")
        self.rbc0 = OWGUI.appendRadioButton( rbbox, self, "rubbish_bins", "Rubbish Bins")
        self.rbc0 = OWGUI.appendRadioButton( rbbox, self, "traffic_light", "Traffic Light")
        self.rbc0 = OWGUI.appendRadioButton( rbbox, self, "traffic_sign", "Traffic Sign")
        OWGUI.separator(tab)

        self.listWidget = OWGUI.listBox(box, self,"listValues","listLabels", callback=self.apply_if)
        OWGUI.button(box, self, 'Open', callback=self.load_file)
        #OWGUI.button(box, self, 'Open File', callback=self.load_file)
        OWGUI.separator(tab)

        OWGUI.lineEdit(tab, self, "lat", box="Latitude")
        OWGUI.lineEdit(tab, self, "lon", box="Longitude")
        OWGUI.button(tab, self, 'Find Lat/Lon', callback=self.use_lat_lon)
        OWGUI.separator(tab)
        tab = OWGUI.createTabPage(self.tabs, "Connection")
        box = OWGUI.widgetBox(tab, "Connection")
        OWGUI.separator(tab)
        OWGUI.lineEdit(tab, self, "server", box="Server")
        OWGUI.lineEdit(tab, self, "key", box="Key")
        OWGUI.lineEdit(tab, self, "secret", box="Secret")
        OWGUI.lineEdit(tab, self, "service", box="Service URL")
        OWGUI.lineEdit(tab, self, "tile", box="Tile URL")
        OWGUI.lineEdit(tab, self, "coverage", box="Coverage URL")
        OWGUI.separator(tab)
        OWGUI.hSlider(tab, self, 'img_width',
                      label='Width:', minValue=128, maxValue=2048)
        OWGUI.hSlider(tab, self, 'img_height',
                      label='Height:', minValue=128, maxValue=2048)
        OWGUI.spin(tab, self, 'fov', min=10,
                   max=180, step=10, label='Field of View:')
        OWGUI.spin(tab, self, 'sr', min=10,
                   max=80, step=10, label='Search Radius:')
        OWGUI.spin(tab, self, 'mr', min=1,
                   max=10, step=1, label='Max Results:')
        #OWGUI.checkBox(tab, self, 'dot', "Do Occulsion Test")
        OWGUI.checkBox(tab, self, 'fqi', "Fetch Quality Information")


    def load_file(self):
        filenames = OWGUI.QFileDialog.getOpenFileNames(self,
                          caption='Select images...', directory='.',
                          filter="Text Files (*.txt *.csv)")
        for fname in filenames:
            text = open(str(fname)).readlines()
            self.loc_list = [line for line in text]
            self.listLabels = self.loc_list

    def load_file(self):
        images = []
        filenames = OWGUI.QFileDialog.getOpenFileNames(self,
                          caption='Select images...', directory='.',
                          filter="Text Files (*.txt *.csv)")
        for fname in filenames:
            text = open(str(fname)).readlines()
            self.loc_list = [line for line in text]
            self.listLabels = self.loc_list


    def use_lat_lon(self):
        images = []
        lat = float(str(self.lat).strip())
        lon = float(str(self.lon).strip())
        pano_id = self.panos.closest(lat,lon)
        f_lat = self.panos[pano_id]['lat'][:13]
        f_lon = self.panos[pano_id]['lon'][:17]
        f_alt = self.panos[pano_id]['alt']
        f_yaw = float(self.panos[pano_id]['yaw'])
        # set the view
        self.view.set(lat, lon, f_alt, width=self.img_width, height=self.img_height, fov=self.fov)
        #view.set(lat, lon, f_alt, width, height, fov)
        diff = (f_yaw - float(self.view.yaw()))/2
        while abs(diff) > 0.1:
            self.view.pan(diff)
            diff = (f_yaw - float(self.view.yaw()))/2
        self.view.pan("45")
        images.append(self.view.get_image())
        self.process_images(images)
        self.send('Images', self.images)
        self.settings_changed = False


    def apply_if(self):
        if self.auto_apply:
            self.apply()
        else:
            self.settings_changed = True

    def apply(self):
        img = self.view.get_image()
        self.process_images([img])
        self.send('Images', self.images)
        self.settings_changed = False

    def apply(self):
        images = []
        elements = self.loc_list[self.listValues[0]].split(",")
        lat = float(elements[0].strip())
        lon = float(elements[1].strip())
        pano_id = self.panos.closest(lat,lon)
        f_lat = self.panos[pano_id]['lat'][:13]
        f_lon = self.panos[pano_id]['lon'][:17]
        f_alt = self.panos[pano_id]['alt']
        f_yaw = float(self.panos[pano_id]['yaw'])
        # set the view
        self.view.set(lat, lon, f_alt, width=self.img_width, height=self.img_height, fov=self.fov)
        #view.set(lat, lon, f_alt, width, height, fov)
        diff = (f_yaw - float(self.view.yaw()))/2
        while abs(diff) > 0.1:
            self.view.pan(diff)
            diff = (f_yaw - float(self.view.yaw()))/2
        images.append(self.view.get_image())
        self.process_images(images)
        self.send('Images', self.images)
        self.settings_changed = False

    def process_images(self, images):
        self.data = images
        if images is not None:
            self.images = [OrangeImage(image) for image in images]
            self.create_thumbnails()
            #self.infoa.setText('%d image(s) processed' % len(self.images))

    def update_images(self):
        if self.data:
            self.process_images(self.data)


if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWEarthmine()
    ow.show()
    appl.exec_()
