import sys
import json
import os
import numpy as np
import cv2

from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                               QVBoxLayout, QWidget, QHBoxLayout)
from PySide2.QtCore import Slot, Qt, QSize
from PySide2.QtGui import QPixmap, QImage

'''
def pixMaptoNumpy(pixmap):
    image = pixmap.toImage()
    b = image.bits()
    b.setsize(self._height * self._width * channels_count)
    arr = np.frombuffer(b, np.uint8).reshape((self._height, self._width, channels_count))
    return arr
'''

def numpytoPixMap(cvImg):
    height, width, channel = cvImg.shape
    bytesPerLine = 3 * width
    qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
    return QPixmap(qImg)

class Magic:
    def __init__(self, numb, objs, lists, result, scale, color = None):
        self.scale = scale
        self.numb = numb
        self.objs = objs
        self.lists = lists
        self.paths = None
        self.setLabel()
        self.result = result
        self.color = color

    @Slot()
    def __call__(self):
        print('click', self.numb)
        prev = False
        self.paths = self.lists(skip = False)

        if self.color is not None:
            color = self.color
            if self.color == 'Raw':
                color = None
            self.setLabel(color = color, skip = False)
            return 

        if self.numb == 'none':
            print(self.paths[0], 'none')
            self.result.newResult(self.paths[0], 'none')
        elif self.numb == 'prev':
            prev = True
        else:
            print(self.paths[0], self.paths[self.numb])
            self.result.newResult(self.paths[0], self.paths[self.numb])
        self.setLabel(prev = prev)
        if prev:
            self.result.deleteResult(self.paths[0])

    def setLabel(self, prev = False, color = 'Gray', skip = True):
        self.paths = self.lists(prev = prev, skip = skip)
        x, y = self.scale
        if color is not None:
            RGB = {'White': (255, 255, 255),
                   'Black': (0, 0, 0),
                   'Blue': (255 * 0.8, 0, 0),
                   'Green': (0, 255 * 0.8, 0),
                   'Red': (0, 0, 255 * 0.8),
                   'Gray': (127.5, 127.5, 127.5)}
            img = cv2.imread(self.paths[0])

            pixmap = QPixmap(self.paths[0])
            pixmap = pixmap.scaled(x, y, Qt.KeepAspectRatio)
            self.objs[0].setPixmap(pixmap)

            h, w = img.shape[:2]
            bg = np.array(RGB[color])[None, None, :]
            for i in range(1, len(self.paths)):
                alpha = cv2.imread(self.paths[i])
                alpha = alpha / 255

                show = img * alpha + bg * (1 - alpha)

                pixmap = numpytoPixMap(show.astype('uint8'))
                pixmap = pixmap.scaled(x, y, Qt.KeepAspectRatio)

                self.objs[i].setPixmap(pixmap)
        else:
            for obj, path in zip(self.objs, self.paths):
                pixmap = QPixmap(path)
                # alpha = cv2.imread(path)
                # pixmap = numpytoPixMap(alpha)
                pixmap = pixmap.scaled(x, y, Qt.KeepAspectRatio)

                obj.setPixmap(pixmap)



class MyWidget(QWidget):
    def __init__(self, imageList, result = None, buttonName = None):
        n = imageList.getN()
        # col = int((n + 1) ** 0.5)
        col = 2
        row = (n + col - 1) // col
        self.scale = (340, 400)
        imgx, imgy = self.scale

        QWidget.__init__(self)

        self.texts = []
        self.buttons = []
        for i in range(n):
            text = QLabel("None")
            text.setFixedSize(QSize(imgx, imgy))
            self.texts.append(text)

        if buttonName is None:
            button_name = [str(i) for i in range(1, n)]
        for i in range(n):
            if i > 0:
                button = QPushButton(buttonName[i - 1])
                self.buttons.append(button)

                self.buttons[i].clicked.connect(Magic(i, self.texts, imageList, result, scale = self.scale))
            else:
                self.buttons.append(None)

        self.cancel = QPushButton('None')
        self.cancel.clicked.connect(Magic('none', self.texts, imageList, result, scale = self.scale))
        self.prev = QPushButton('Previous')
        self.prev.clicked.connect(Magic('prev', self.texts, imageList, result, scale = self.scale))
        self.toolButtons = [self.cancel, self.prev]
        colors = ['Gray', 'Blue', 'Green', 'Red', 'Black', 'White', 'Raw']
        for color in colors:
            temp = QPushButton(color)
            temp.clicked.connect(Magic(color, self.texts, imageList, result, color = color, scale = self.scale))
            self.toolButtons.append(temp)

        self.layouts = []
        for x, y in zip(self.buttons, self.texts):
            temp = QVBoxLayout()
            temp.addWidget(y)
            if x is not None:
                temp.addWidget(x)
            self.layouts.append(temp)

        imageLayout = QVBoxLayout()
        for i in range(col):
            temp = QHBoxLayout()
            for j in self.layouts[i * row: (i + 1) * row]:
                temp.addLayout(j)
            imageLayout.addLayout(temp)

        buttonLayout = QVBoxLayout()
        for button in self.toolButtons:
            buttonLayout.addWidget(button)

        self.mainLayout = QHBoxLayout()
        self.mainLayout.addLayout(imageLayout)
        self.mainLayout.addLayout(buttonLayout)

        self.setLayout(self.mainLayout)

class InputImages:
    def __init__(self, fileList, result = None):
        self.file = open(fileList, 'r')
        self.lists = []
        for line in self.file:
            self.lists.append(line[:-1].split(' '))
        self.n = len(self.lists[0])
        self.cnt = 0
        self.total = len(self.lists)
        self.result = result


    def __call__(self, prev = False, skip = True):
        if prev:
            while self.cnt > 0:
                self.cnt -= 1
                if len(self.lists[self.cnt]) == self.n:
                    break
            now = self.lists[self.cnt]
            return now

        while True:
            if self.cnt == self.total:
                self.result.dumpResult()
                exit(0)
            if len(self.lists[self.cnt]) != self.n:
                continue
            now = self.lists[self.cnt]
            if skip and self.result is not None and self.result.checkResult(now[0]):
                self.cnt += 1
                continue
            return now
    
    def getN(self):
        return self.n

class Result:
    def __init__(self, path):
        if os.path.exists(path):
            fin = open(path, 'r')
            self.map = json.load(fin)
            fin.close()
        else:
            self.map = {}
        self.path = path

    def newResult(self, inputImage, chooseImage):
        self.map[inputImage] = chooseImage

    def deleteResult(self, inputImage):
        self.map.pop(inputImage)

    def checkResult(self, inputImage):
        if inputImage in self.map:
            return True
        else:
            return False

    def dumpResult(self):
        import json
        fout = open(self.path, 'w')
        json.dump(self.map, fout)
        fout.close()

if __name__ == "__main__":
    res = Result('output.txt')
    inp = InputImages('list.txt', result = res)
    app = QApplication(sys.argv)
    name = 'closedform  closedform_facetri  deep  deep2  deep2_facetri  deep_facetri  shared  shared_facetri'.split('  ')

    widget = MyWidget(imageList = inp, result = res, buttonName = name)
    # widget.resize(800, 600)
    widget.show()

    t = app.exec_()
    res.dumpResult()
    sys.exit(t)
