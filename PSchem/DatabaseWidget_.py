from PyQt4 import QtCore, QtGui
from Database.Primitives import *
import os

class DatabaseModel(QtCore.QAbstractItemModel):
    def __init__(self, database, parent=None):
        QtCore.QAbstractItemModel.__init__(self, parent)
        self.database = database
        database.installUpdateHook(self)

    def update(self):
        print 'aaa'
        self.reset()
    #    self.dataChanged(QtCore.QModelIndex(), QtCore.QModelIndex())

    def data(self, index, role):
        #print 'data:', index, role, index.internalPointer(), index.row(), index.column()
        if not index.isValid():
            return QtCore.QVariant()

        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        row = index.row()
        #print row
        #if not 0 <= row < self.rowCount(index.parent()):
        #    return QtCore.QVariant()

        col = index.column()
        #print col
        data = index.internalPointer()
        #print 'data:', data
        #return QtCore.QVariant('database')
        if isinstance(data, Database):
            return QtCore.QVariant('database')
        elif isinstance(data, Library):
            if col == 0:
                return QtCore.QVariant(data.name())
            else:
                return QtCore.QVariant('library')
        elif isinstance(data, Cell):
            if col == 0:
                return QtCore.QVariant(data.name())
            else:
                return QtCore.QVariant('cell')
        elif isinstance(data, CellView):
            if col == 0:
                return QtCore.QVariant(data.name())
            else:
                return QtCore.QVariant('cellview')
        elif isinstance(data, Element):
            if col == 0:
                return QtCore.QVariant(data.name())
            else:
                return QtCore.QVariant('element')
        else:
            return QtCore.QVariant()


    def index(self, row, column, parent):
        #print 'index:', row, column, parent, parent.internalPointer(), parent.row(), parent.column()
        #if row < 0 or column < 0 or row >= self.rowCount(parent) or column >= self.columnCount(parent):
        #    return QtCore.QModelIndex()

        data = None
        if parent.isValid():
            data = parent.internalPointer()

        #print 'index:', data
        #if data is None or isinstance(data, Database):
        if not parent.isValid() or isinstance(data, Database):
            children = list(self.database.libraries())
        elif isinstance(data, Library):
            children = list(data.cells())
        elif isinstance(data, Cell):
            children = list(data.views())
        elif isinstance(data, CellView):
            children = list(data.elems())
        else:
            return QtCore.QModelIndex()

        children.sort(lambda a, b: cmp(a.name(), b.name()))
        #print 'Index', children[row], children[row].name()
        if children[row]._idx is None:
            children[row]._idx = self.createIndex(row, column, children[row])
        return children[row]._idx
            #return self.createIndex(row, column, children[row])

    def parent(self, index):
        #print 'parent:', index, index.internalPointer(), index.row(), index.column()
        if not index.isValid():
            return QtCore.QModelIndex()

        data = index.internalPointer()
        if isinstance(data, Database):
            return QtCore.QModelIndex()
        elif isinstance(data, Library):
            d = list(data.parent().libraries())
            d.sort()
            n = d.index(data)
            #print 'Parent', data.parent(), n, d[n].name()
            return QtCore.QModelIndex()
            #return self.createIndex(n, 0, data.parent())
            #return self.createIndex(n, 0, d[n].name())
    #return self.createIndex(n, 0, data.parent())
        elif isinstance(data, Cell):
            d = list(data.parent().cells())
            d.sort()
            n = d.index(data)
            #print 'Parent', data.parent(), n, d[n].name()
            #print d, n
            #return self.createIndex(n, 0, d.name())
            return data.parent()._idx
            #return self.createIndex(n, 0, data.parent())
        elif isinstance(data, CellView):
            d = list(data.parent().views())
            d.sort()
            n = d.index(data)
            return data.parent()._idx
        elif isinstance(data, Element):
            d = list(data.parent().elems())
            d.sort()
            n = d.index(data)
            return data.parent()._idx
        else:
            return QtCore.QModelIndex()

    def hasChildren(self, parent):
        #print 'haschildren:', parent, parent.internalPointer(), parent.row(), parent.column()
        #print parent.data()
        if not parent.isValid():
            return True
        data = parent.internalPointer()
        if isinstance(data, Database):
            return len(data.libraries()) > 0
        elif isinstance(data, Library):
            return len(data.cells()) > 0
        elif isinstance(data, Cell):
            return len(data.views()) > 0
        elif isinstance(data, CellView):
            return len(data.elems()) > 0
        else:
            return False

    def rowCount(self, parent):
        #return 1
        #print 'row count:', parent, parent.internalPointer(), parent.row(), parent.column()
        if parent.column() > 1:
            return 0

        #print parent.data()
        if not parent.isValid():
            return len(self.database.libraries())

        data = parent.internalPointer()
        if isinstance(data, Database):
            return len(data.libraries())
        elif isinstance(data, Library):
            return len(data.cells())
        elif isinstance(data, Cell):
            return len(data.views())
        elif isinstance(data, CellView):
            return len(data.elems())
        else:
            return 0

    def columnCount(self, parent):
        #print 'col count:', parent, parent.internalPointer(), parent.row(), parent.column()
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
            return 1
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

    def flagsaaa(self, index):
    
        """flags(self, index)
        
        Returns the flags for the item corresponding to the given index.
        
        All items are enabled by default.
        """
        
        if not index.isValid():
            return QtCore.QAbstractItemModel.flags(self, index)
        
        return QtCore.Qt.ItemIsEnabled

class DatabaseWidget(QtGui.QTreeView):
    def __init__(self, parent=None):
        QtGui.QTreeView.__init__(self, parent)
        #self.model = DatabaseModel(None)
        #self.setModel(self.model)
        #self.setRootIndex(self.model.index(0, 0, os.getcwd()))
        #self.setRootIsDecorated(False)
        #self.setSortingEnabled(True)
        #for i in range(1, self.model.columnCount()):
        #    self.setColumnHidden(i, True)
        #self.setHeader(self.header().setSectionHidden(2, True))
        #self.setWordWrap(True)
        #self.setHeaderHidden(True)
        #self.setAnimated(True)
