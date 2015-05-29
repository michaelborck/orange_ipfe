import OWGUI
from OWWidget import OWWidget
from PyQt4.QtGui import QSizePolicy
from ImgViewer import ImageViewer
from PyQt4.QtCore import Qt, QAbstractListModel, QVariant

# Not strong on Qt programming, from what I
# can determine the abstract list model
# allows me to list images.

class PreviewListModel(QAbstractListModel):

    def __init__(self):
        QAbstractListModel.__init__(self)
        self.index = self.createIndex(0, 0)
        self.images = []

    def data(self, model_index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return ""
        if role == Qt.DecorationRole:
            return self.images[model_index.row()]
        else:
            return QVariant()

    def rowCount(self, parent=0):  # No unerscores, overide rowCount()
        return len(self.images)

    def insert(self, image):
        # Inserts `count` rows before `index`.
        self.beginInsertRows(self.index, self.rowCount(), 1)
        self.images.append(image)
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows(self.index, 0, len(self.images))
        self.images = []
        self.endRemoveRows()


class OWImgWidget(OWWidget):

    def __init__(self, *args, **kwargs):
        super(OWImgWidget, self).__init__(*args, **kwargs)

        self.model = PreviewListModel()

        # GUI
        self.preview = OWGUI.QListView(self.mainArea)
        self.preview.setModel(self.model)
        self.preview.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview.setViewMode(OWGUI.QListView.IconMode)
        self.preview.setResizeMode(OWGUI.QListView.Adjust)
        self.mainArea.layout().addWidget(self.preview)
        self.preview.clicked.connect(self.display_selected)

    def create_thumbnails(self, height=150):
        self.model.clear()
        for image in self.images:
            self.model.insert(image.thumbnail(height=height))

    def display_selected(self, index):
        # If available use the matplotlib viewer.  It provides
        # most of functionality need.  Similar to how Orange
        # allows you to select rows of a data table I want to be able
        # to select images, and/or regions within those images.
        # Suspect will have to write own, perhaps even modify/change
        # ImgViewer to display one image at a time with next/back
        # buttons.
        row = index.row()
        image = self.images[row]

        qt_image = image.qimage()
        viewer = ImageViewer(qt_image)
        viewer.show()
        return
        if image:
            try:  # use pylab plot. zoom,save, etc already provided
                from matplotlib.plot import imshow, gray, show, axes
                imshow(image.data, interpolation="none")
                ax1 = axes()
                ax1.axes.get_yaxis().set_visible(False)
                ax1.axes.get_xaxis().set_visible(False)
                gray()
                show()  # TODO: Not use QT main loop
            except:  # else use basic viewer #TODO Look at Data/OWImageViewer
                qt_image = image.qimage()
                viewer = ImageViewer(qt_image)
                viewer.show()
        else:
            print 'OWImgWidget:disaply_selected: image is None'
