"""
<name>Array to Table</name>
<description>Convert a numpy array into a table </description>
<icon>icons/arraytotable.png</icon>
<contact>Michael Borck (michael(@at@)borck.id.au)</contact>
<priority>130</priority>
"""

import Orange
import OWGUI
from OWWidget import *
import numpy as np


class OWArrayToTable(OWWidget):

    def __init__(self, parent=None, signalManager=None):
        super(OWArrayToTable, self).__init__(parent, signalManager)

        # Inputs/Outputs
        self.inputs = [('Images', list, self.process_images)]
        self.outputs = [('Data', ExampleTable)]

        # Instance attributes
        self.data = None

    def process_images(self, images):
        if images != None:
            image_list = [np.array(image.data) for image in images]
            self.data = Orange.data.Table(image_list[0])
        self.send('Data', self.data)

if __name__ == '__main__':
    appl = OWGUI.QApplication([__name__])
    ow = OWArrayToTable()
    ow.show()
    appl.exec_()
