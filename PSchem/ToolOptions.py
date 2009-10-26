# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from FlowLayout import *

class ToolOptions(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self._topLayout = QtGui.QVBoxLayout()
        self._titleLabel = QtGui.QLabel()
        self._topLayout.addWidget(self._titleLabel)
        self._layout = FlowLayout()
        #self._layout = QtGui.QVBoxLayout()
        self._topLayout.addLayout(self._layout)
        self.setLayout(self._topLayout)

    def makeGrid(self):
        group = QtGui.QGroupBox()
        group.setTitle("Grid")
        layout = QtGui.QFormLayout()
        layout.setVerticalSpacing(0)
        layout.setMargin(4)
        visible = QtGui.QCheckBox('Visible')
        layout.addRow('', visible)
        snapValue = QtGui.QLineEdit('1.0')
        layout.addRow('Spacing', snapValue)
        group.setLayout(layout)
        return group
        
    def setTitle(self, text):
        self._titleLabel.setText(text)

    def layout(self):
        return self._layout

class SelectToolOptions(ToolOptions):
    def __init__(self):
        ToolOptions.__init__(self)
        self.setTitle('Selection Tool')
        self.layout().addWidget(self.makeSelectMode())
        self.layout().addWidget(self.makeSelectOverlap())
        self.layout().addWidget(self.makeGrid())


    def makeSelectMode(self):
        group = QtGui.QGroupBox()
        group.setTitle("Select Mode")
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(4)
        partialMode = QtGui.QRadioButton('Partial')
        fullMode = QtGui.QRadioButton('Full')
        layout.addWidget(partialMode)
        layout.addWidget(fullMode)
        group.setLayout(layout)
        return group
        
    def makeSelectOverlap(self):
        group = QtGui.QGroupBox()
        group.setTitle('Select Shapes')
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(4)
        encl = QtGui.QRadioButton('Enclosed')
        ovrl = QtGui.QRadioButton('Overlapping')
        layout.addWidget(encl)
        layout.addWidget(ovrl)
        group.setLayout(layout)
        return group





