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

import Globals
Qt = __import__(Globals.UI,  globals(),  locals(),  ['QtCore',  'QtGui'])
QtCore = Qt.QtCore
QtGui = Qt.QtGui

#from PyQt4 import QtCore, QtGui
from Database.Cells import *
from Database.CellViews import *
from PSchem.ConsoleWidget import Command
import os

class LibraryHierarchyModel(QtCore.QAbstractItemModel):
    def __init__(self, libraries, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        #self.modelThread = QtCore.QThread()
        #self.modelThread.start()
        #self.moveToThread(self.modelThread)
        self.libraries = libraries
        libraries.libraryViewAdded(self)
        #print 'model ', self.thread()

    def prepareForUpdate(self):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))

    def update(self):
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        #self.reset()
        #self.dataChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def data(self, index, role):
        if not index.isValid():
            return None
            #return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole and role != QtCore.Qt.ToolTipRole:
            return None
            #return QtCore.QVariant()

        row = index.row()

        col = index.column()
        data = index.internalPointer()
        if isinstance(data, Libraries):
            return self.tr('Libraries')
            #return QtCore.QVariant('libraries')
        if col == 0:
            if role == QtCore.Qt.DisplayRole:
                return data.name
                #return QtCore.QVariant(data.name)
            else: #role == QtCore.Qt.ToolTipRole:
                if isinstance(data, Libraries) or isinstance(data, Library):
                    return data.path
                    #return QtCore.QVariant(data.path)
                elif isinstance(data, Cell):
                    return data.library.path + "/" + data.name
                    #return QtCore.QVariant(data.library.path + "/" + data.name)
                elif isinstance(data, CellView):
                    return data.library.path + "/" + data.cell.name + "/" + data.name
                    #return QtCore.QVariant(data.library.path + "/" + data.cell.name + "/" + data.name)
        elif isinstance(data, Library):
            return self.tr('Library')
            #return QtCore.QVariant('library')
        elif isinstance(data, Cell):
            return self.tr('Cell')
            #return QtCore.QVariant('cell')
        elif isinstance(data, Schematic):
            return self.tr('Schematic')
            #return QtCore.QVariant('schematic')
        elif isinstance(data, Symbol):
            return self.tr('Symbol')
            #return QtCore.QVariant('symbol')
        elif isinstance(data, CellView):
            return self.tr('Cell View')
            #return QtCore.QVariant('cellview')
        else:
            return None
            #return QtCore.QVariant()


    def index(self, row, column, parent):
        data = None
        if parent.isValid():
            data = parent.internalPointer()

        if not parent.isValid() or isinstance(data, Libraries):
            children = self.libraries.sortedLibraries
        elif isinstance(data, Library):
            children = data.sortedLibraries + data.sortedCells
        elif isinstance(data, Cell):
            children = data.sortedCellViews
        else:
            return QtCore.QModelIndex()

        if row >= 0 and len(children) > row:
            return self.createIndex(row, column, children[row])
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        data = index.internalPointer()
        if isinstance(data, Libraries):
            return QtCore.QModelIndex()
        elif isinstance(data, Library):
            parentLibrary = data.parentLibrary
            if parentLibrary:
                pParentLibrary = parentLibrary.parentLibrary
                if pParentLibrary:
                    d = pParentLibrary.sortedLibraries + pParentLibrary.sortedCells
                else:
                    d = self.libraries.sortedLibraries
                n = d.index(parentLibrary)
                return self.createIndex(n, 0, parentLibrary)
            return QtCore.QModelIndex()
        elif isinstance(data, Cell):
            parentLibrary = data.library.parentLibrary
            if parentLibrary:
                d = parentLibrary.sortedLibraries + parentLibrary.sortedCells
            else:
                d = self.libraries.sortedLibraries
            n = d.index(data.library)
            return self.createIndex(n, 0, data.library)
        elif isinstance(data, CellView):
            d = data.library.sortedCells
            n = d.index(data.cell)
            return self.createIndex(n, 0, data.cell)
        else:
            return QtCore.QModelIndex()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True
        data = parent.internalPointer()
        if isinstance(data, Libraries):
            return len(data.sortedLibraries) > 0
        elif isinstance(data, Library):
            return len(data.sortedLibraries) + len(data.sortedCells) > 0
        elif isinstance(data, Cell):
            return len(data.sortedCellViews) > 0
        else:
            return False

    def rowCount(self, parent):
        if parent.column() > 1:
            return 0

        if not parent.isValid():
            return len(self.libraries.sortedLibraries)

        data = parent.internalPointer()
        if isinstance(data, Libraries):
            return len(data.sortedLibraries)
        elif isinstance(data, Library):
            return len(data.sortedLibraries) + len(data.sortedCells)
        elif isinstance(data, Cell):
            return len(data.sortedCellViews)
        else:
            return 0

    def columnCount(self, parent):
        if not parent.isValid():
            return 2
        data = parent.internalPointer()
        if isinstance(data, Libraries):
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
                return self.tr('Name')
                #eturn QtCore.QVariant(self.tr("Name"))
            elif section == 1:
                return self.tr('Type')
                #eturn QtCore.QVariant(self.tr("Type"))
            #elif section == 2:
            #    return self.tr('Value')
            #    return QtCore.QVariant(self.tr("Value"))
            else:
                return None
                #return QtCore.QVariant()

        return None
        #return QtCore.QVariant()

class LibraryHierarchyWidget(QtGui.QWidget):
    def __init__(self, window, model):
        QtGui.QWidget.__init__(self, window)
        self.window = window
        self.model = model
        
        self.treeView = QtGui.QTreeView()
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAlternatingRowColors(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.treeView)

        self.treeView.setModel(model)

        self.connect(self.treeView,
                     #QtCore.SIGNAL("doubleClicked(QModelIndex)"),
                     QtCore.SIGNAL("activated(QModelIndex)"),
                     self.openCellView)

        self.setLayout(layout)

    def openCellView(self, index):
        if not index.isValid():
            return

        data = index.internalPointer()

        if isinstance(data, CellView):
            self.window.controller.execute(
                Command(
                    'window.openDatabaseObjectByPathName(\'' + data.path + '\')'))

    def selectedCellView(self):
        return self.model.libraries.objectByPath(Path.createFromPathName('examples.gTAG/gTAG/schematic'))

