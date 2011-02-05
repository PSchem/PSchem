# -*- coding: utf-8 -*-

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

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
from Database.Layers import *
from Database.Cells import *
from PSchem.LayerView import *
from random import random

class LayerModel(QtCore.QAbstractItemModel):
    def __init__(self, layersView, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.layersView = layersView
        layersView.installUpdateViewsHook(self)

    def update(self):
        self.emit(QtCore.SIGNAL("layoutChanged()"))

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.DecorationRole and role != QtCore.Qt.CheckStateRole:
            return QtCore.QVariant()

        row = index.row()

        col = index.column()
        data = index.internalPointer()
        if isinstance(data, LayerView) and role == QtCore.Qt.DecorationRole:
            if col == 0:
                return QtCore.QVariant(data.icon)
                #return QtCore.QVariant(QtGui.QColor(random()*255,
                #                                    random()*255,
                #                                    random()*255,
                #                                    ))
                #return QtCore.QVariant(QtGui.QColor(QtCore.Qt.red))
        elif isinstance(data, LayerView) and role == QtCore.Qt.CheckStateRole:
            layer = data.layer
            if col == 1:
                if layer.visible:
                    return QtCore.QVariant(QtCore.Qt.Checked)
                else:
                    return QtCore.QVariant(QtCore.Qt.Unchecked)
            elif col == 2:
                if layer.selectable:
                    return QtCore.QVariant(QtCore.Qt.Checked)
                else:
                    return QtCore.QVariant(QtCore.Qt.Unchecked)
        elif isinstance(data, LayerView) and role == QtCore.Qt.DisplayRole:
            layer = data.layer
            if col == 3:
                return QtCore.QVariant(layer.name)
            elif col == 4:
                return QtCore.QVariant(layer.type)
        return QtCore.QVariant()

    def index(self, row, column, parent):

        if not parent.isValid():
            children = list(self.layersView.layerViews)
        else:
            return QtCore.QModelIndex()

        children.sort(lambda a, b: cmp(a.layer.zValue, b.layer.zValue))
        return self.createIndex(row, column, children[row])

    def parent(self, index):
        return QtCore.QVariant()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True
        return False

    def rowCount(self, parent):
        if not parent.isValid():
            return len(self.layersView.layerViews)
        return 0

    def columnCount(self, parent):
        if not parent.isValid():
            return 5
        return 0

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return QtCore.QVariant(self.tr(""))
            elif section == 1:
                return QtCore.QVariant(self.tr("V"))
            elif section == 2:
                return QtCore.QVariant(self.tr("S"))
            elif section == 3:
                return QtCore.QVariant(self.tr("Name"))
            elif section == 4:
                return QtCore.QVariant(self.tr("Type"))
            else:
                return QtCore.QVariant()
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


class LayerTreeView(QtGui.QTreeView):
    def __init__(self):
        QtGui.QTreeView.__init__(self)

class LayerWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.proxyModel = ProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        #self.header = QtGui.QHeaderView(QtCore.Qt.Horizontal)
        self.treeView = LayerTreeView()
        #self.treeView.setHeader(self.header)
        self.treeView.header().setDefaultSectionSize(32)
        self.treeView.header().resizeSection(2, 32)
        #self.treeView.header().moveSection(2, 3)
        #self.header.setResizeMode(
        #     0, QtGui.QHeaderView.Fixed)
        self.treeView.header().setResizeMode(
            0, QtGui.QHeaderView.Fixed)
        #self.treeView.header().setResizeMode(
        #    2, QtGui.QHeaderView.ResizeToContents)
        self.treeView.setSortingEnabled(False)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setRootIsDecorated(False)
        
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
        #self.treeView.setModel(model)


