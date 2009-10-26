# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from Database.Primitives import *

class LayerModel(QtCore.QAbstractItemModel):
    def __init__(self, layers, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.layers = layers
        layers.installUpdateInstanceViewsHook(self)

    def update(self):
        self.reset()

    def data(self):
        return QtCore.QVariant()

    def index(self, row, column, parent):
        return QtCore.QVariant()

    def parent(self, index):
        return QtCore.QVariant()

    def hasChildren(self, parent):
        return False

    def rowCount(self, parent):
        return 0

    def headerData(self, section, orientation, role):
        return QtCore.QVariant()

class ProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self):
        QtGui.QSortFilterProxyModel.__init__(self)
        self.libRegExp = QtCore.QRegExp()
        self.cellRegExp = QtCore.QRegExp()

    def filterAcceptsRow(self, row, parent):
        source_idx = self.sourceModel().index(row, 0, parent)

        if not source_idx.isValid():
            return True

        data = source_idx.internalPointer()
        if isinstance(data, Library) and not self.libRegExp.isEmpty():
            text = self.sourceModel().data(
                source_idx, QtCore.Qt.DisplayRole).toString()
            return text.contains(self.libRegExp)
        elif isinstance(data, Cell) and not self.cellRegExp.isEmpty():
            text = self.sourceModel().data(
                source_idx, QtCore.Qt.DisplayRole).toString()
            return text.contains(self.cellRegExp)
        else:
            return True

    def setRegExps(self, libRegExp, cellRegExp):
        self.libRegExp = libRegExp
        self.cellRegExp = cellRegExp


class LayerWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.proxyModel = ProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.treeView = QtGui.QTreeView()
        self.treeView.setSortingEnabled(True)

        layout2 = QtGui.QHBoxLayout()
        self.libFilterText = QtGui.QLineEdit()
        self.cellFilterText = QtGui.QLineEdit()
        layout2.addWidget(QtGui.QLabel('Lib'))
        layout2.addWidget(self.libFilterText)
        layout2.addWidget(QtGui.QLabel('Cell'))
        layout2.addWidget(self.cellFilterText)

        layout = QtGui.QVBoxLayout()
        layout.addLayout(layout2)
        layout.addWidget(self.treeView)

        self.connect(self.libFilterText,
                     QtCore.SIGNAL("textChanged(QString)"),
                     self.updateRegExp)
        self.connect(self.cellFilterText,
                     QtCore.SIGNAL("textChanged(QString)"),
                     self.updateRegExp)

        self.setLayout(layout)

    def updateRegExp(self):
        libText = str(self.libFilterText.text())
        cellText = str(self.cellFilterText.text())
        self.proxyModel.setRegExps(
            QtCore.QRegExp(libText, QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.Wildcard),
            QtCore.QRegExp(cellText, QtCore.Qt.CaseInsensitive,
                           QtCore.QRegExp.Wildcard))
        self.proxyModel.invalidateFilter()

    def setSourceModel(self, model):
        self.proxyModel.setSourceModel(model)
        self.treeView.setModel(self.proxyModel)


