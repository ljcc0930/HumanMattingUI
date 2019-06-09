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
            path_list = []
            img_paths = s[0:1]
            tri_paths = s[1:-2]
            res_paths = s[-2:]
            path_list.append(img_paths)
            path_list.append(tri_paths)
            path_list.append(res_paths)
            self.list.append(path_list)

        self.len = len(self.list)
        self.cnt = -1
    
    def __call__(self):
        self.cnt += 1
        if self.cnt >= self.len:
            return None
        imgPaths, triPaths, resPaths = self.list[self.cnt][:3]
        self.nowImg = cv2.imread(imgPaths[0])
        self.candidateTris = []
        if os.path.exists(resPaths[1]):
            self.candidateTris.append(cv2.imread(resPaths[1]))
        else:
            for triPath in triPaths:
                self.candidateTris.append(cv2.imread(triPath))
        self.nowAlpha = None
        if os.path.exists(resPaths[0]):
            self.nowAlpha = cv2.imread(resPaths[0])

        return self.nowImg, self.candidateTris, self.nowAlpha

    def previous(self):
        if self.cnt > 0:
            self.cnt -= 1
            imgPaths, triPaths, resPaths = self.list[self.cnt][:3]
            self.nowImg = cv2.imread(imgPaths[0])
            self.candidateTris = []
            if os.path.exists(resPaths[1]):
                self.candidateTris.append(cv2.imread(resPaths[1]))
            else:
                for triPath in triPaths:
                    self.candidateTris.append(cv2.imread(triPath))
            self.nowAlpha = None
            if os.path.exists(resPaths[0]):
                self.nowAlpha = cv2.imread(resPaths[0])
            if self.nowAlpha is None:
                self.nowAlpha = np.zeros(self.nowImg.shape)

        return self.nowImg, self.candidateTris, self.nowAlpha
    
    def save(self, trimap):
        triPath = self.list[self.cnt][2][1]
        cv2.imwrite(triPath, trimap.astype('uint8'))

    def saveAlpha(self, alpha):
        alphaPath = self.list[self.cnt][2][0]
        cv2.imwrite(alphaPath, alpha)

    def saveBoth(self, alpha, foreground):
        alphaPath = self.list[self.cnt][2][0]
        b_channel, g_channel, r_channel = cv2.split(foreground)
        a_channel = alpha.mean(axis = 2)
        img_bgra = cv2.merge((b_channel, g_channel, r_channel, a_channel))
        cv2.imwrite(alphaPath, img_bgra)
