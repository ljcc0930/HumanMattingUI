import cv2
from PySide2.QtGui import QImage, QPixmap

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
    
    def save(self, trimap):
        imgPath, triPath = self.list[self.cnt][:2]
        cv2.imwrite(triPath, trimap.astype('uint8'))

