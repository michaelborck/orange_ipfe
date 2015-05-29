import Orange
from OWWidget import OWWidget
import OWGUI

# Couldn't use Orange's image viewer as I need one
# that didn't modify the aspect ratio when creating a thumbnail.

class ImageViewer(OWWidget):

    def __init__(self, image):
        super(ImageViewer, self).__init__()

        self.imageLabel = OWGUI.QLabel()
        self.imageLabel.setBackgroundRole(OWGUI.QPalette.Base)
        self.imageLabel.setSizePolicy(
            OWGUI.QSizePolicy.Ignored, OWGUI.QSizePolicy.Ignored)
        self.imageLabel.setSizePolicy(
            OWGUI.QSizePolicy.Expanding, OWGUI.QSizePolicy.Expanding)
        # qsp = OWGUI.QSizePolicy()
        # qsp.setHeightForWidth(True)
        # self.setSizePolicy(qsp)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = OWGUI.QScrollArea()
        self.scrollArea.setBackgroundRole(OWGUI.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        self.setWindowTitle("Image Viewer")
        self.scaleFactor = 1.0
        self.resize(512, 512)
        self.imageLabel.setPixmap(OWGUI.QPixmap.fromImage(image))
        self.mainArea.layout().addWidget(self.imageLabel)


if __name__ == '__main__':
    appl = OWGUI.QApplication([__file__])
    filename = "test.jpg"
    image = OWGUI.QImage(filename)
    imageViewer = ImageViewer(image)
    imageViewer.show()
    appl.exec_()
