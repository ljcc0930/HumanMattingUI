from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
	QPushButton, QRadioButton, QButtonGroup, QDialog)
from PySide2.QtCore import QSize
import cv2
import numpy as np

from utils import numpytoPixmap
import config


class SelectDialog(QDialog):
	def __init__(self, image, trimaps):
		super(SelectDialog, self).__init__()

		self.image = image
		self.candidateTrimaps = trimaps
		self.resize(1200, 800)
		labelW = 400
		h, w = self.image.shape[:2]
		if w > labelW:
			ratio = float(labelW) / float(w)
		else:
			ratio = 1
		labelH = int(h * ratio)
		self.image = cv2.resize(self.image, (labelW, labelH))

		widget = QWidget()
		Vlayout = QVBoxLayout()
		self.buttonGroup = QButtonGroup()
		id = 0
		for trimap in self.candidateTrimaps:
			Hlayout = QHBoxLayout()
			image_label = QLabel()
			image_label.setFixedSize(QSize(labelW, labelH))
			image_label.setPixmap(numpytoPixmap(self.image))
			trimap_label = QLabel()
			trimap_label.setFixedSize(QSize(labelW, labelH))
			trimap_label.setPixmap(numpytoPixmap(trimap))
			fusion_label = QLabel()
			fusion_label.setFixedSize(QSize(labelW, labelH))
			fusion = self.image * 0.5 + trimap * 0.5
			fusion_label.setPixmap(numpytoPixmap(fusion))
			radioButton = QRadioButton(str(id))
			self.buttonGroup.addButton(radioButton, id)
			Hlayout.addWidget(image_label)
			Hlayout.addWidget(trimap_label)
			Hlayout.addWidget(fusion_label)
			Hlayout.addWidget(radioButton)
			Vlayout.addLayout(Hlayout)
			id += 1
		self.button = QPushButton('OK')
		self.button.clicked.connect(self.select)
		Vlayout.addWidget(self.button)
		widget.setLayout(Vlayout)

		scrollArea = QScrollArea()
		scrollArea.setWidget(widget)
		layout = QVBoxLayout(self)
		layout.addWidget(scrollArea)
		self.setLayout(layout)

		self.buttonGroup.button(0).setChecked(True)
		self.selectId = 0

	def select(self):
		self.selectId = self.buttonGroup.checkedId()
		self.accept()