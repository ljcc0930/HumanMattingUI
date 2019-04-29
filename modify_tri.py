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
            imgPath, triPath = self.list[self.cnt][:2]
            self.nowImg = cv2.imread(imgPath)
            self.nowTri = cv2.imread(triPath)
        return self.nowImg, self.nowTri

class EditingImage(QLabel):
    def __init__(self, widget, id, text):
        super(EditingImage, self).__init__(text)
        self.widget = widget
        self.id = id

    def mousePressEvent(self, QMouseEvent):
        self.widget.click(QMouseEvent.pos())

    def mouseMoveEvent(self, QMouseEvent):
        self.widget.drag(QMouseEvent.pos())

    def mouseReleaseEvent(self, QMouseEvent):
        self.widget.release()
    
class MyButton(QPushButton):
    def __init__(self, widget, text):
        super(MyButton, self).__init__(text)
        self.text = text
        self.widget = widget
        self.buttons = {
            'Foreground':   lambda : self.widget.setColor((255, 255, 255)),
            'Background':   lambda : self.widget.setColor((0, 0, 0)),
            'Unknown':      lambda : self.widget.setColor((128, 128, 128)),
            'Undo':         self.widget.undo,
            'Run':          self.widget.run,
            'Save':         self.widget.save,
            'Previous':     lambda : self.widget.newSet(True),
            'Next':         self.widget.newSet
        }

    def mouseReleaseEvent(self, QMouseEvent):
        super(MyButton, self).mouseReleaseEvent(QMouseEvent)
        print(self.text)
        self.buttons[self.text]()


class MyWidget(QWidget):
    def setImage(self, x, pixmap = None, array = None, resize = False):
        if pixmap is None:
            pixmap = numpytoPixmap(array)
        imgx, imgy = self.scale
        if resize:
            pixmap = pixmap.scaled(imgx, imgy, Qt.KeepAspectRatio)
        self.texts[x].setPixmap(pixmap)

    def setSet(self):
        self.setImage(0, array = self.image)
        self.setImage(1, array = self.trimap)
        show = self.image * 0.7 + self.trimap * 0.3
        self.setImage(2, array = show)

    def newSet(self, prev = False):
        if prev:
            self.image, self.trimap = self.imageList.previous()
        else:
            self.image, self.trimap = self.imageList()

        if len(self.trimap.shape) == 2:
            self.trimap = np.stack([self.trimap] * 3, axis = 2)
        assert self.image.shape == self.trimap.shape

        h, w = self.image.shape[:2]
        imgw, imgh = self.scale
        self.f = min(imgw / w, imgh / h)

        self.image = cv2.resize(self.image, None, fx = self.f, fy = self.f)
        self.trimap = cv2.resize(self.trimap, None, fx = self.f, fy = self.f)
        self.history = []
        self.setSet()

    def resizeToNormal(self):
        f = 1 / self.f
        image = cv2.resize(self.image, None, fx = f, fy = f)
        trimap = cv2.resize(self.trimap, None, fx = f, fy = f)
        return image, trimap

    def undo(self):
        if len(self.history) > 0:
            self.trimap = self.history.pop()
            self.setSet()

    def save(self):
        # TODO
        raise Exception("Undefined!")

    def run(self):
        for i, func in enumerate(self.functions):
            image, trimap = self.resizeToNormal()
            output = func(image, trimap)
            self.setImage(i + 3, array = output, resize = True)


    def click(self, pos):
        self.history.append(self.trimap.copy())
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

    def release(self):
        pass

    def initImageLayout(self):
        n, row, col = self.n, self.row, self.col
        imgx, imgy = self.scale
        self.texts = []
        for i in range(3):
            text = EditingImage(self, i, "None")
            text.setAlignment(Qt.AlignTop)
            text.setFixedSize(QSize(imgx, imgy))
            self.texts.append(text)

        for i in self.functions:
            text = QLabel("")
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
        toolTexts = 'Foreground Background Unknown Undo Run Save Previous Next'.split(' ')
        self.toolWidgets = []

        for text in toolTexts:
            temp = MyButton(self, text)
            self.toolWidgets.append(temp)

        self.toolLayout = QVBoxLayout()
        for tool in self.toolWidgets:
            self.toolLayout.addWidget(tool)

    def setColor(self, color):
        self.color = color

    def __init__(self, imageList, functions):
        QWidget.__init__(self)

        self.functions = functions
        self.history = []

        self.imageList = imageList
        self.scale = (500, 400)
        self.n = 3 + len(functions)
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


def main(inputList, *args):
    inp = ImageInputs(inputList)
    app = QApplication(sys.argv)

    widget = MyWidget(imageList = inp, functions = args)
    # widget.resize(800, 600)
    widget.show()

    t = app.exec_()
    sys.exit(t)


if __name__ == "__main__":
    a = lambda x, y : y
    main('list.txt', a)
