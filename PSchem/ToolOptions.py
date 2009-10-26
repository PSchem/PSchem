# -*- coding: utf-8 -*-

# This file is part of PSchem.
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with PSchem.  If not, see <http://www.gnu.org/licenses/>.

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





