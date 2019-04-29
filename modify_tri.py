import sys
import json
import os
import numpy as np
import cv2

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QHBoxLayout)
from PySide2.QtCore import Slot, Qt, QSize
from PySide2.QtGui import QPixmap, QImage, QCursor

def numpytoPixmap(cvImg):
    cvImg = cvImg.astype('uint8')
    height, width, channel = cvImg.shape
    bytesPerLine = 3 * width
    qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
    return QPixmap(qImg)

class ImageInputs:
    def __init__(self, path):
        fin = open(path, 'r')
        self.list = []
        for line in fin:
            s = line[:-1].split(' ')
            self.list.append(s)

        self.len = len(self.list)
        self.cnt = -1
    
    def __call__(self):
        self.cnt += 1
        if self.cnt >= self.len:
            return None
        imgPath, triPath = self.list[self.cnt][:2]
        self.nowImg = cv2.imread(imgPath)
        self.nowTri = cv2.imread(triPath)
        return self.nowImg, self.nowTri

    def previous(self):
        if self.cnt > 0:
            self.cnt -= 1
            self.nowImg = cv2.imread(imgPath)
            self.nowTri = cv2.imread(triPath)
        return self.nowImg, self.nowTri

class EditingImage(QLabel):
    def __init__(self, widget, id, *args, **kwargs):
        super(EditingImage, self).__init__(*args, **kwargs)
        self.widget = widget
        self.id = id

    def mousePressEvent(self, QMouseEvent):
        self.widget.click(QMouseEvent.pos())

    def mouseMoveEvent(self, QMouseEvent):
        self.widget.drag(QMouseEvent.pos())

    def mouseReleaseEvent(self, QMouseEvent):
        pass
    
'''
class MyButton(QButton):
    def __init__(self, widget, id, *args, **kwargs):
        super(MyButton, self).__init__(*args, **kwargs)
        self.widget = widget
'''


class MyWidget(QWidget):
    def setImage(self, x, pixmap = None, array = None):
        if pixmap is None:
            pixmap = numpytoPixmap(array)
        imgx, imgy = self.scale
        # pixmap = pixmap.scaled(imgx, imgy, Qt.KeepAspectRatio)
        self.texts[x].setPixmap(pixmap)

    def setSet(self):
        self.setImage(0, array = self.image)
        self.setImage(1, array = self.trimap)
        show = self.image * 0.7 + self.trimap * 0.3
        self.setImage(2, array = show)

    def newSet(self):
        self.image, self.trimap = self.imageList()
        if len(self.trimap.shape) == 2:
            self.trimap = np.stack([self.trimap] * 3, axis = 2)
        assert self.image.shape == self.trimap.shape

        h, w = self.image.shape[:2]
        imgw, imgh = self.scale
        f = min(imgw / w, imgh / h)

        self.image = cv2.resize(self.image, None, fx = f, fy = f)
        self.trimap = cv2.resize(self.trimap, None, fx = f, fy = f)
        self.setSet()

    def click(self, pos):
        x, y = pos.x(), pos.y()
        self.mousePosition = x, y
        cv2.line(self.trimap, (x, y), (x, y), self.color, 
                 thickness = self.thickness)
        self.setSet()

    def drag(self, pos):
        x, y = pos.x(), pos.y()
        cv2.line(self.trimap, self.mousePosition, (x, y), self.color, 
                 thickness = self.thickness)
        self.mousePosition = x, y
        self.setSet()

    def initImageLayout(self):
        n, row, col = self.n, self.row, self.col
        imgx, imgy = self.scale
        self.texts = []
        for i in range(n):
            # text = QLabel("None")
            text = EditingImage(self, i, "None")
            text.setAlignment(Qt.AlignTop)
            text.setFixedSize(QSize(imgx, imgy))
            self.texts.append(text)
        self.newSet()

        self.imageLayout = QVBoxLayout()
        for i in range(row):
            rowLayout = QHBoxLayout()
            for j in self.texts[i * col: (i + 1) * col]:
                rowLayout.addWidget(j)
            self.imageLayout.addLayout(rowLayout)

    def initToolLayout(self):
        toolTexts = 'Foreground Background Unknown Run Previous Next Save'.split(' ')
        self.toolWidgets = []

        for text in toolTexts:
            temp = QPushButton(text)
            # TODO: add button connection
            # temp.clicked.connect()
            self.toolWidgets.append(temp)


        self.toolLayout = QVBoxLayout()
        for tool in self.toolWidgets:
            self.toolLayout.addWidget(tool)

    def __init__(self, imageList):
        QWidget.__init__(self)

        self.imageList = imageList
        self.scale = (500, 400)
        self.n = 6
        self.row = 2
        self.col = (self.n + self.row - 1) // self.row

        self.color = (128, 128, 128)
        self.thickness = 5
        self.mousePosition = None

        self.initImageLayout()
        self.initToolLayout()


        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.imageLayout)
        self.mainLayout.addLayout(self.toolLayout)

        self.setLayout(self.mainLayout)



if __name__ == "__main__":
    inp = ImageInputs('list.txt')
    app = QApplication(sys.argv)

    widget = MyWidget(imageList = inp)
    # widget.resize(800, 600)
    widget.show()

    t = app.exec_()
    sys.exit(t)
