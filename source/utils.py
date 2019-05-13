import cv2
import os
import numpy as np

from PySide2.QtGui import QImage, QPixmap
from PySide2.QtWidgets import QLayout, QLabel,QVBoxLayout
from PySide2.QtCore import QSize

def numpytoPixmap(cvImg):
    cvImg = cvImg.astype('uint8')
    height, width, channel = cvImg.shape
    bytesPerLine = 3 * width
    qImg = QImage(cvImg.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()
    return QPixmap(qImg)

def addBlankToLayout(layout, blankSize):
    assert isinstance(layout, QLayout)
    blank = QLabel("")
    if isinstance(layout, QVBoxLayout):
        blank.setFixedSize(QSize(1, blankSize))
    else:
        blank.setFixedSize(QSize(blankSize, 1))
    layout.addWidget(blank)

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
        imgPath, triPath, alphaPath = self.list[self.cnt][:3]
        self.nowImg = cv2.imread(imgPath)
        self.nowTri = cv2.imread(triPath)
        self.nowAlpha = None
        if os.path.exists(alphaPath):
            self.nowAlpha = cv2.imread(alphaPath)

        return self.nowImg, self.nowTri, self.nowAlpha

    def previous(self):
        if self.cnt > 0:
            self.cnt -= 1
            imgPath, triPath, alphaPath = self.list[self.cnt][:3]
            self.nowImg = cv2.imread(imgPath)
            self.nowTri = cv2.imread(triPath)
            self.nowAlpha = None
            if os.path.exists(alphaPath):
                self.nowAlpha = cv2.imread(alphaPath)
            if self.nowAlpha is None:
                self.nowAlpha = np.zeros(self.nowImg.shape)

        return self.nowImg, self.nowTri, self.nowAlpha
    
    def save(self, trimap):
        imgPath, triPath = self.list[self.cnt][:2]
        cv2.imwrite(triPath, trimap.astype('uint8'))

    def saveAlpha(self, alpha):
        alphaPath = self.list[self.cnt][2]
        cv2.imwrite(alphaPath, alpha)

