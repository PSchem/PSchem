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
from Database.Primitives import *
from Database.Design import *
#import sys

class DesignHierarchyModel(QtCore.QAbstractItemModel):
    def __init__(self, designs, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self._designs = designs
        designs.installUpdateHierarchyViewsHook(self)

    @property
    def designs(self):
        return self._designs
        
    def prepareForUpdate(self):
        self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))

    def update(self):
        self.emit(QtCore.SIGNAL("layoutChanged()"))
        #self.reset()

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        row = index.row()

        col = index.column()
        data = index.internalPointer()
        if isinstance(data, Design):
            if col == 0:
                return QtCore.QVariant('')
            elif col == 1:
                return QtCore.QVariant(data.cellView.cell.name)
            else:
                return QtCore.QVariant(data.cellView.library.path)
        elif isinstance(data, DesignUnit):
            if col == 0:
                return QtCore.QVariant(data.instance.name)
            elif col == 1:
                return QtCore.QVariant(data.instance.instanceCellName)
            else:
                return QtCore.QVariant(data.instance.instanceLibraryPath)
        else:
            return QtCore.QVariant()


    def index(self, row, column, parent):

        data = None
        if parent.isValid():
            data = parent.internalPointer()

        if not parent.isValid() or isinstance(data, Designs):
            children = self.designs.sortedDesigns
        elif isinstance(data, DesignUnit):
            children = data.sortedChildDesignUnits #+ list(data.pins()) + list(data.nets() - data.pins())
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
        if isinstance(data, Design):
            return QtCore.QModelIndex()
        if isinstance(data, DesignUnit):
            parent = data.parentDesignUnit
            #sys.stderr.write('parent' + parent.cellView.cell.name + "\n")
            if parent:
                pparent = parent.parentDesignUnit
                if pparent:
                    #sys.stderr.write('pparent' + pparent.cellView.cell.name + "\n")
                    d = pparent.sortedChildDesignUnits
                    n = d.index(parent)
                    return self.createIndex(n, 0, parent)
                else:
                    d = list(self.designs.sortedDesigns)
                    n = d.index(parent)
                    return self.createIndex(n, 0, parent)
        return QtCore.QModelIndex()

    def hasChildren(self, parent):
        if not parent.isValid():
            return True
        data = parent.internalPointer()
        if isinstance(data, DesignUnit):
            return len(data.sortedChildDesignUnits) > 0
        else:
            return False

    def rowCount(self, parent):
        #if parent.column() > 1:
        #    return 0

        if not parent.isValid():
            return len(self.designs.sortedDesigns)

        data = parent.internalPointer()
        if isinstance(data, DesignUnit):
            return len(data.sortedChildDesignUnits) #+ list(data.pins) + list(data.nets - data.pins)
        return 0

    def columnCount(self, parent):
        if not parent.isValid():
            return 3
        data = parent.internalPointer()
        if isinstance(data, DesignUnit):
            return 3
        return 0


    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if section == 0:
                return QtCore.QVariant(self.tr("Instance"))
            elif section == 1:
                return QtCore.QVariant(self.tr("Cell"))
            elif section == 2:
                return QtCore.QVariant(self.tr("Library"))
            else:
                return QtCore.QVariant()

        return QtCore.QVariant()

class DesignHierarchyWidget(QtGui.QWidget):
    def __init__(self, window, model):
        QtGui.QWidget.__init__(self, window)
        self.window = window
        self.model = model

        self.treeView = QtGui.QTreeView()
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAlternatingRowColors(True)

        self.treeView.setModel(model)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.treeView)

        self.setLayout(layout)


