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
from Database.Cells import *
from Database.CellViews import *
from PSchem.ConsoleWidget import Command
import os

class DatabaseModel(QtCore.QAbstractItemModel):
    def __init__(self, database, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        #self.modelThread = QtCore.QThread()
        #self.modelThread.start()
        #self.moveToThread(self.modelThread)
        self.database = database
        database.installUpdateDatabaseViewsHook(self)
        #print 'model ', self.thread()

    def prepareForUpdate(self):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))

    def update(self):
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        #self.reset()
        #self.dataChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.ToolTipRole:
            return QtCore.QVariant()

        row = index.row()

        col = index.column()
        data = index.internalPointer()
        if isinstance(data, Database):
            return QtCore.QVariant('database')
        if col == 0:
            return QtCore.QVariant(data.name())
        elif isinstance(data, Library):
            return QtCore.QVariant('library')
        elif isinstance(data, Cell):
            return QtCore.QVariant('cell')
        elif isinstance(data, Schematic):
            return QtCore.QVariant('schematic')
        elif isinstance(data, Symbol):
            return QtCore.QVariant('symbol')
        elif isinstance(data, CellView):
            return QtCore.QVariant('cellview')
        else:
            return QtCore.QVariant()


    def index(self, row, column, parent):
        data = None
        if parent.isValid():
            data = parent.internalPointer()

        if not parent.isValid() or isinstance(data, Database):
            children = list(self.database.libraries())
        elif isinstance(data, Library):
            children = list(data.libraries()) + list(data.cells())
        elif isinstance(data, Cell):
            children = list(data.cellViews())
        else:
            return QtCore.QModelIndex()

        #children.sort(lambda a, b: cmp(a.name(), b.name()))
        if row >= 0 and len(children) > row:
            return self.createIndex(row, column, children[row])
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        data = index.internalPointer()
        if isinstance(data, Database):
            return QtCore.QModelIndex()
        elif isinstance(data, Library):
            parentLibrary = data.parentLibrary()
            if parentLibrary:
                pParentLibrary = parentLibrary.parentLibrary()
                if pParentLibrary:
                    d = list(pParentLibrary.libraries()) + list(pParentLibrary.cells())
                else:
                    d = list(self.database.libraries())
                n = d.index(parentLibrary)
                return self.createIndex(n, 0, parentLibrary)
            return QtCore.QModelIndex()
        elif isinstance(data, Cell):
            parentLibrary = data.library().parentLibrary()
            if parentLibrary:
                d = list(parentLibrary.libraries()) + list(parentLibrary.cells())
            else:
                d = list(self.database.libraries())
            #d = list(data.library().cells())
            #d = list(self.database.libraries())
            #d.sort(lambda a, b: cmp(a.name(), b.name()))
            n = d.index(data.library())
            return self.createIndex(n, 0, data.library())
        elif isinstance(data, CellView):
            d = list(data.library().cells())
            #d.sort(lambda a, b: cmp(a.name(), b.name()))
            n = d.index(data.cell())
            return self.createIndex(n, 0, data.cell())
        else:
            return QtCore.QModelIndex()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True
        data = parent.internalPointer()
        if isinstance(data, Database):
            return len(data.libraries()) > 0
        elif isinstance(data, Library):
            return len(data.libraries()) + len(data.cells()) > 0
        elif isinstance(data, Cell):
            return len(data.cellViews()) > 0
        else:
            return False

    def rowCount(self, parent):
        if parent.column() > 1:
            return 0

        #print parent.data()
        if not parent.isValid():
            return len(self.database.libraries())

        data = parent.internalPointer()
        if isinstance(data, Database):
            return len(data.libraries())
        elif isinstance(data, Library):
            return len(data.libraries()) + len(data.cells())
        elif isinstance(data, Cell):
            return len(data.cellViews())
        else:
            return 0

    def columnCount(self, parent):
        if not parent.isValid():
            return 2
        data = parent.internalPointer()
        if isinstance(data, Database):
            return 2
        elif isinstance(data, Library):
            return 2
        elif isinstance(data, Cell):
            return 2
        elif isinstance(data, CellView):
            return 2
        else:
            return 0


    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return QtCore.QVariant(self.tr("Name"))
            elif section == 1:
                return QtCore.QVariant(self.tr("Type"))
            #elif section == 2:
            #    return QtCore.QVariant(self.tr("Value"))
            else:
                return QtCore.QVariant()

        return QtCore.QVariant()

class ProxyModel(QtGui.QSortFilterProxyModel):
    def __init__(self):
        QtGui.QSortFilterProxyModel.__init__(self)
        self.libRegExp = QtCore.QRegExp()
        self.cellRegExp = QtCore.QRegExp()
        #print 'proxy ', self.thread()

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


class DatabaseWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #print 'view ', self.thread()
        self.window = parent
        self.proxyModel = ProxyModel()
        self.proxyModel.setDynamicSortFilter(True)
        self.sourceModel = None
        self.treeView = QtGui.QTreeView()
        self.treeView.setSortingEnabled(True)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAlternatingRowColors(True)
        #self.treeView.setAllColumnsShowFocus(True)
        
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
        self.connect(self.treeView,
                     #QtCore.SIGNAL("doubleClicked(QModelIndex)"),
                     QtCore.SIGNAL("activated(QModelIndex)"),
                     self.openCellView)

        self.setLayout(layout)

    def openCellView(self, index):
        indexSource = self.proxyModel.mapToSource(index)
        if not indexSource.isValid():
            return

        data = indexSource.internalPointer()

        if isinstance(data, CellView):
            #if self.window:
                cell = data.cell()
                lib = cell.library()
                self.window.controller.execute(
                    Command(
                        'window.openCellViewByName(\'' +lib.path()+
                        '\', \''+cell.name()+'\', \''+data.name()+'\')'))


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
        self.sourceModel = model
        self.proxyModel.setSourceModel(model)
        self.treeView.setModel(self.proxyModel)
        #self.treeView.setModel(self.sourceModel)

    def selectedCellView(self):
        #return self.sourceModel.database.cellViewByName('latch', 'comparator', 'schematic')
        #return self.sourceModel.database.cellViewByName('latch', 'analoglatch', 'schematic')
        return self.sourceModel.database.cellViewByName('/examples/gTAG', 'gTAG', 'schematic')
    #return None

