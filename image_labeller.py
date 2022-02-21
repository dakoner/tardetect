import sys
import glob
import os
import signal
import pandas
import sqlite3
from PyQt5 import QtGui, QtCore, QtWidgets
NO_STATE = 0
RESIZE = 1

IMAGE_DIR=r"z:\tardigrade movies\Untitled Project"

#con = sqlite3.connect(os.path.join(IMAGE_DIR, "labels.sqlite")
#labels = pandas.Dataframe(columns={"image", "label", "coords"})
def get_main_window()       :
    tlw = QtWidgets.qApp.topLevelWidgets()
    for item in tlw:
        if isinstance(item, MainWindow):
            return item


def createIcon(name, size=(25,25)):
    pixmap = QtGui.QPixmap(*size)
    pixmap.fill(getattr(QtGui.QColorConstants.Svg, name))
    return QtGui.QIcon(pixmap)

class LabelListView(QtWidgets.QListView):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setModel(model)
        
                
        self.colors = [name for name in QtGui.QColorConstants.Svg.__dict__ if not name.startswith("_")]

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openMenu) 

        filename = "labels.txt"
        items = [line.strip() for line in open(filename).readlines()]
        self.clearAndAddItems(items)

    def clearAndAddItems(self, elements):
        self.model().clear()
        for i, element in enumerate(elements):
            item = QtGui.QStandardItem(createIcon(self.colors[i]), element)
            self.model().appendRow(item)

    def openMenu(self, position):
        menu = QtWidgets.QMenu()
        addAction = menu.addAction("Add")
        loadAction = menu.addAction("Load")
        saveAction = menu.addAction("Save")
        action = menu.exec_(self.mapToGlobal(position))
        if action == addAction:
            self.addItem()
        elif action == loadAction:
            self.loadLabels()
        elif action == saveAction:
            self.saveLabels()

    def loadLabels(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Load labels')[0]
        items = [line.strip() for line in open(filename).readlines()]
        self.clearAndAddItems(items)

    def saveLabels(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save labels')[0]
        open(filename, "w").write('\n'.join([self.model().item(i).text() for i in range(self.model().rowCount())]))

    def addItem(self):
        item = QtGui.QStandardItem("unknown")
        self.model().appendRow(item)
       


class ImageLabelView(QtWidgets.QListView):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setModel(model)
        self.selectionModel().selectionChanged.connect(self.selection_changed)

    def selection_changed(self, selected, deselected):
        item = self.model().itemFromIndex(selected.indexes()[0])
        item.rect.setPen(QtGui.QPen(QtCore.Qt.red))
        if len(deselected.indexes()):
            item = self.model().itemFromIndex(deselected.indexes()[0])
            item.rect.setPen(QtGui.QPen(QtCore.Qt.black))


class QGraphicsRectItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
        self.state = NO_STATE
 
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if bool(event.modifiers() & QtCore.Qt.ControlModifier):
                main_window = get_main_window()
                main_window.scene.removeItem(self)
                event.accept()
                return
            else:
                sp = event.scenePos()
                if QtGui.QVector2D(sp - self.sceneBoundingRect().bottomRight()).length() < 25:
                    self.state = RESIZE
                    event.accept()
                    return
                
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if bool(event.modifiers() & QtCore.Qt.ControlModifier):
            event.ignore()
            return
        
        if (event.buttons() & QtCore.Qt.LeftButton):
            if self.state == RESIZE:
                r = self.rect()
                d = event.pos() - event.lastPos()
                r.adjust(0, 0, d.x(), d.y())
                self.setRect(r)
                event.accept()
                return
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if bool(event.modifiers() & QtCore.Qt.ControlModifier):
                event.accept()
                return
            else:
                self.state = NO_STATE
        super().mouseReleaseEvent(event)
        
class QGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start = None
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

class QGraphicsScene(QtWidgets.QGraphicsScene):
    def __init__(self, main_window, label_view, image_label_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # could main_window be parent?
        self.setParent(main_window)
        self.main_window = main_window
        self.label_view = label_view
        self.image_label_model = image_label_model
        
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if bool(event.modifiers() & QtCore.Qt.ControlModifier):
                event.accept()
                return
            else:
                if not self.mouseGrabberItem():
                    end = event.scenePos()
                    start = event.buttonDownScenePos(QtCore.Qt.LeftButton)
            
                    # action = menu.exec_(self.mapToGlobal(position))
                    labels = [self.label_view.model().item(i).text() for i in range(self.label_view.model().rowCount())]
                    rect = QtCore.QRectF(QtCore.QPointF(0.,0.), end-start)
                    box = QGraphicsRectItem(rect)
                    color = QtGui.QColor(255, 255, 255, 30)
                    box.setBrush(QtGui.QBrush(color))
                    box.setPos(start)
                    self.addItem(box)
                    label, okPressed = QtWidgets.QInputDialog.getItem(self.main_window, "Set label", 
                                                        "Label:", labels, 0, False)
                    if okPressed and label != '':
                        item = QtGui.QStandardItem(label)
                        item.rect = box
                        rect.item = item
                        name = self.label_view.colors[labels.index(label)]
                        color = getattr(QtGui.QColorConstants.Svg, name)
                        box.setPen(QtGui.QPen(color))
                        self.image_label_model.appendRow(item)
                        
                        text = self.addSimpleText(label)
                        text.setPen(QtGui.QPen(color))
                        text.setBrush(QtGui.QBrush(color))
                        text.setParentItem(box)
                        text.setPos(rect.topRight())
                    else:
                        self.removeItem(box)

        super().mouseReleaseEvent(event)

        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.statusBar().showMessage("Test")
        
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.label_list_model = QtGui.QStandardItemModel(self)
        self.label_view = LabelListView(self.label_list_model)
        self.image_label_model = QtGui.QStandardItemModel(self)     
        self.image_label_view = ImageLabelView(self.image_label_model)
        

        self.view = QGraphicsView()
        self.view.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.scene = QGraphicsScene(self, self.label_view, self.image_label_model)
        self.view.setScene(self.scene)


        self.control_widget = QtWidgets.QWidget(self)
        self.forward_button = QtWidgets.QPushButton('forward')
        self.forward_button.clicked.connect(self.forward)
        self.backward_button = QtWidgets.QPushButton('backward')
        self.backward_button.clicked.connect(self.backward)
        self.control_layout = QtWidgets.QHBoxLayout()
        self.control_layout.addWidget(self.forward_button)
        self.control_layout.addWidget(self.backward_button)
        self.control_widget.setLayout(self.control_layout)


        self.list_widget = QtWidgets.QWidget(self)
        list_layout = QtWidgets.QVBoxLayout()
        list_layout.addWidget(self.label_view)
        list_layout.addWidget(self.image_label_view)
        self.list_widget.setLayout(list_layout)

        central_layout = QtWidgets.QHBoxLayout()
        self.central_widget.setLayout(central_layout)
        central_layout.addWidget(self.list_widget)

        central_layout.addWidget(self.view)
        central_layout.addWidget(self.control_widget)





        exitAction = QtWidgets.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        saveLabelsAction = QtWidgets.QAction(QtGui.QIcon('saveLabels.png'), '&Save labels', self)
        saveLabelsAction.setStatusTip('SaveImage')
        saveLabelsAction.setShortcut('Ctrl+S')
        saveLabelsAction.triggered.connect(self.saveLabels)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveLabelsAction)
        fileMenu.addAction(exitAction)

        self.currentItem = None

        filenames = glob.glob(os.path.join(IMAGE_DIR, "*.png"))
        filenames.sort()
        #filenames = QtWidgets.QFileDialog.getOpenFileNames(self, 'Open Files')[0]
        self.loadImageFrames(filenames)

    def forward(self, event):
        if self.index < len(self.filenames):
            self.index = self.index + 1
            self.readImageFrame()
    
        
    def backward(self, event):
        if self.index > 0:
            self.index = self.index - 1
            self.readImageFrame()
        

    def loadImageFrames(self, filenames=None):
        self.filenames = filenames
        self.index = 0
        self.readImageFrame()

    def readImageFrame(self):
        self.statusBar().showMessage("%d of %d frames" % (self.index, len(self.filenames)))
        filename = self.filenames[self.index]
        image = QtGui.QImage(filename, 'ARGB32')
        pixmap = QtGui.QPixmap(image)
        if self.currentItem != None:
            self.currentItem.setPixmap(pixmap)
        else:
            self.currentItem = self.scene.addPixmap(pixmap)
        self.currentItem.filename = filename
        
    def saveLabels(self):
        if self.currentItem:
            filename = self.currentItem.filename
            labels_filename = filename + ".labels"
            with open(labels_filename, "w") as f:
                for item in self.scene.items():
                    if isinstance(item, QGraphicsRectItem):
                        p = item.pos()
                        w = self.currentItem.pixmap().width()
                        h = self.currentItem.pixmap().height()
                        label = item.childItems()[0].text()
                        f.write("np.array([[%f,%f,%f,%f]], dtype=np.float32),\n" % (p.x()/w, p.y()/h, (p.x()+item.rect().width())/w, (p.y()+item.rect().height())/h))

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    app.exec_()
