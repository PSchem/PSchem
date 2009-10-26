# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

# Port of a FlowLayout Qt example
# (with some extensions)

class FlowLayout(QtGui.QLayout):
    def __init__(self, parent=None, margin=None, spacing=None):
        QtGui.QLayout.__init__(self, parent)
        self.items = []
        if margin:
            self.setMargin(margin)
        if spacing:
            self.setSpacing(spacing)

    def addItem(self, item):
        self.items.append(item)

    def itemAt(self, index):
        if index >= 0 and index < len(self.items):
            return self.items[index]
        else:
            return None

    def count(self):
        return len(self.items)

    def expandingDirections(self):
        return QtCore.Qt.Vertical | QtCore.Qt.Horizontal

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QtCore.QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        QtGui.QLayout.setGeometry(self, rect)
        self.doLayout(rect, False)

    def minimumSize(self):
        size = QtCore.QSize()
        for i in self.items:
            size = size.expandedTo(i.minimumSize())

        size = size + QtCore.QSize(2*self.margin(), 2*self.margin())
        return size

    def sizeHint(self):
        return self.minimumSize()

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for i in self.items:
            widget = i.widget()
            spaceX = self.spacing() + widget.style().layoutSpacing(
                QtGui.QSizePolicy.PushButton,
                QtGui.QSizePolicy.PushButton,
                QtCore.Qt.Horizontal)
            spaceY = self.spacing() + widget.style().layoutSpacing(
                QtGui.QSizePolicy.PushButton,
                QtGui.QSizePolicy.PushButton,
                QtCore.Qt.Vertical)
            nextX = x + i.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + i.sizeHint().width() + spaceX
                lineHeight = 0


            if not testOnly:
                i.setGeometry(QtCore.QRect(QtCore.QPoint(x, y),
                                           i.sizeHint()))

            # reducing width of a widget if larger that available area
            if not testOnly and rect.width() < i.sizeHint().width():
                i.setGeometry(
                    QtCore.QRect(QtCore.QPoint(x, y),
                                 QtCore.QSize(rect.width(),
                                              i.sizeHint().height())))

            x = nextX
            lineHeight = max(lineHeight, i.sizeHint().height())

        return y + lineHeight - rect.y()

