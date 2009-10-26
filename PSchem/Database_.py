from PyQt4 import QtCore, QtGui


class DatabaseModel(QtGui.QDirModel):
    def __init__(self, parent=None):
        QtGui.QDirModel.__init__(self, parent)

#class DatabaseModel(QtGui.QDirModel):
#    def __init__(self):
#        pass

#class DatabaseView(QtGui.QTreeView):
#    pass
    #def __init__(self):
    #    pass
        #QtGui.QTreeView.__init__(self)
        #self.model = DatabaseModel()
        #self.setModel(self.model)
