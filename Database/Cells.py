# -*- coding: utf-8 -*-

# Copyright (C) 2009 PSchem Contributors (see CONTRIBUTORS for details)

# This file is part of PSchem Database
 
# PSchem is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# PSchem is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with PSchem Database.  If not, see <http://www.gnu.org/licenses/>.

#print 'Cells in'

#from Database.CellViews import *
from Database.Design import *
from xml.etree import ElementTree as et

#print 'Cells out'

class Cell():

    @classmethod
    def createCell(cls, name, library):
        """Construct a Library object, or return an existing one."""
        if name in library.cellNames:
            self = library.cellNames[name]
        else:
            self = cls()
            self._cellViews = set()
            self._cellViewNames = {}
            self._name = name
            self._library = library
            self._sortedCellViews = None
            library.cellAdded(self)
        return self

    @property
    def cellViews(self):
        return self._cellViews

    @property
    def cellViewNames(self):
        return self._cellViewNames

    @property
    def name(self):
        return self._name

    @property
    def library(self):
        return self._library
        
    @property
    def database(self):
        return self.library.database

    @property
    def implementation(self):
        schematic = self.cellViewByName('schematic')  #currently assume it is 'schematic'
        if schematic:
            return schematic
        return self.cellViewByName('symbol')

    @property
    def symbol(self):
        return self.cellViewByName('symbol')  #currently assume it is 'symbol'

    @property
    def sortedCellViews(self):
        if not self._sortedCellViews:
            self._sortedCellViews = sorted(self.cellViews, lambda a, b: cmp(a.name.lower(), b.name.lower()))
        return self._sortedCellViews

    def cellViewByName(self, cellViewName):
        if self.cellViewNames.has_key(cellViewName):
            return self.cellViewNames[cellViewName]
        else:
            return None

    def cellViewAdded(self, cellView):
        self.cellViews.add(cellView)
        self.cellViewNames[cellView.name] = cellView
        self._sortedCellViews = None
        self.library.cellChanged(self)

    def cellViewRemoved(self, cellView):
        self.cellViews.remove(cellView)
        del self.cellViewNames[cellView.name]
        self._sortedCellViews = None
        self.library.cellChanged(self)
        
    def cellViewChanged(self, cellView):
        self.library.cellChanged(self)

    def remove(self):
        for c in list(self.cellViews):
            c.remove()
        self.library.cellRemoved(self)
        self.library = None

class Library():

    @classmethod
    def createLibrary(cls, name, database, parentLibrary = None):
        """Construct a Library object, or return an existing one."""
        if parentLibrary:
            parent = parentLibrary
        else:
            parent = database
        if name in parent.libraryNames:
            self = parent.libraryNames[name]
        else:
            self = cls()
            self._cells = set()
            self._cellNames = {}
            self._libraries = set()
            self._libraryNames = {}
            self._parentLibrary = parentLibrary
            self._name = name
            self._database = database
            self._sortedLibraries = None
            self._sortedCells = None
            parent.libraryAdded(self)
        return self

    @property
    def cells(self):
        return self._cells

    @property
    def cellNames(self):
        return self._cellNames

    @property
    def libraries(self):
        return self._libraries

    @property
    def libraryNames(self):
        return self._libraryNames

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        if self.parentLibrary:
            return self.parentLibrary.path + '/' + self.name
        else:
            return '/' + self.name

    @property
    def database(self):
        if not self._database:
            self._database = self.parentLibrary.database
        return self._database
        
    @property
    def parentLibrary(self):
        return self._parentLibrary
        
    @property
    def sortedLibraries(self):
        """Cached list of libraries sorted by name."""
        if not self._sortedLibraries:
            #self._sortedChildNames = (self.libraryNames.keys() + self.cellNames.keys()).sort(key=str.lower) #lambda a, b: cmp(a.name.lower(), b.name.lower()))
            #self._sortedChildNames = sorted(self.libraryNames.keys() + self.cellNames.keys()) #.sort(key=str.lower) #lambda a, b: cmp(a.name.lower(), b.name.lower()))
            self._sortedLibraries = sorted(self.libraries, lambda a, b: cmp(a.name.lower(), b.name.lower()))
            #self._sortedLibraries = self.libraries
        return self._sortedLibraries

    @property
    def sortedCells(self):
        """Cached list of cells sorted by name."""
        if not self._sortedCells:
            #self._sortedChildNames = (self.libraryNames.keys() + self.cellNames.keys()).sort(key=str.lower) #lambda a, b: cmp(a.name.lower(), b.name.lower()))
            #self._sortedChildNames = sorted(self.libraryNames.keys() + self.cellNames.keys()) #.sort(key=str.lower) #lambda a, b: cmp(a.name.lower(), b.name.lower()))
            self._sortedCells = sorted(self.cells, lambda a, b: cmp(a.name.lower(), b.name.lower()))
            #self._sortedCells = self.cells
        return self._sortedCells

    def cellAdded(self, cell):
        self.cells.add(cell)
        self.cellNames[cell.name] = cell
        self._sortedCells = None
        self.database.libraryChanged(self)

    def cellRemoved(self, cell):
        self.cells.remove(cell)
        del self.cellNames[cell.name]
        self._sortedCells = None
        self.database.libraryChanged(self)
        
    def cellChanged(self, cell):
        self.database.libraryChanged(self)

    def libraryAdded(self, library):
        self.libraries.add(library)
        self.libraryNames[library.name] = library
        self._sortedLibraries = None
        self.database.libraryChanged(self)

    def libraryRemoved(self, library):
        self.libraries.remove(library)
        del self.libraryNames[library.name]
        self._sortedLibraries = None
        self.database.libraryChanged(self)
        
    def libraryChanged(self, library):
        self.database.libraryChanged(self)

    def libraryByPath(self, libraryPath):
        (first, sep, rest) = libraryPath.partition('/')
        if first == '..':
            return self.parentLibrary.libraryByPath(rest)
        elif first == '.':
            return self.libraryByPath(rest)
        elif first == '':
            return self.database.libraryByPath(rest)
        elif self.libraryNames.has_key(first):
            if rest == '':
                return self.libraryNames[first]
            else:
                return self.libraryNames[first].libraryByPath(rest)
        else:
            return None

    @classmethod
    def concatenateLibraryPaths(cls, libPath1, libPath2):
        (beginning1, sep, last1) = libPath1.rpartition('/')
        (first2, sep, rest2) = libPath2.partition('/') 
        if libPath2.find('/') == 0: #is absolute
            return libPath2
        elif len(libPath2) == 0:
            return libPath1
        elif first2 == '.':
            return Library.concatenateLibraryPaths(libPath1, rest2)
        elif first2 == '..' and beginning1 != '':
            return Library.concatenateLibraryPaths(beginning1, rest2)
        elif first2 == '..':
            return '/' + libPath2
        else:
            return libPath1 + '/' + libPath2

    def cellByName(self, cellName):
        if self.cellNames.has_key(cellName):
            return self.cellNames[cellName]
        else:
            return None

    def cellViewByName(self, cellName, cellViewName):
        cell = self.cellByName(cellName)
        if cell:
            return cell.cellViewByName(cellViewName)
        else:
            return None

    def remove(self):
        # remove child libraries&cells
        for c in list(self.cells):
            c.remove()
        for l in list(self.libraries):
            l.remove()
        # notify parent library or database
        if self.parentLibrary:
            self.parentLibrary.libraryRemoved(self)
        else:
            self.database.libraryRemoved(self)
        self.parentLibrary = None
        self.database = None
        

class Database():
    theDatabase = None

    @classmethod
    def createDatabase(cls, client):
        """Construct a Database object, or return an existing one."""
        if Database.theDatabase:
            self = Database.theDatabase
            #self._client = client
        else:
            self = cls()
            Database.theDatabase = self
            self._client = client
            self._libraries = set()
            self._libraryNames = {}
            self._databaseViews = set()
            self._layers = None
            self._designs = Designs(self)
            self._deferredProcessingObjects = set()
            self._sortedLibraries = None
        return self
    
    @property
    def client(self):
        return self._client
        
    @property
    def libraries(self):
        return self._libraries

    @property
    def libraryNames(self):
        return self._libraryNames

    @property
    def layers(self):
        return self._layers
        
    @layers.setter
    def layers(self, layers):
        self._layers = layers
        #self.updateViews()

    @property
    def designs(self):
        return self._designs

    @property
    def databaseViews(self):
        return self.databaseViews

    @property
    def path(self):
        return '/'

    @property
    def sortedLibraries(self):
        """Cached list of libraries sorted by name."""
        if not self._sortedLibraries:
            self._sortedLibraries = sorted(self.libraries, lambda a, b: cmp(a.name.lower(), b.name.lower()))
        #print self._sortedLibraries
        return self._sortedLibraries

    def installUpdateDatabaseViewsHook(self, view):
        self._databaseViews.add(view)

    def updateDatabaseViewsPreparation(self):
        """
        Some views may require notification before layout
        of the database changes
        """
        for v in self._databaseViews:
            v.prepareForUpdate()
        
    def updateDatabaseViews(self):
        "Notify views that the database layout has changed"
        for v in self._databaseViews:
            v.update()

    def updateDatabaseViewsPreparation(self):
        """
        Some views may require notification before layout
        of the design hierarchy changes
        """
        for v in self._databaseViews:
            v.prepareForUpdate()
        
    def libraryAdded(self, library):
        self.libraries.add(library)
        self.libraryNames[library.name] = library
        self._sortedLibraries = None
        self.requestDeferredProcessing(self)

    def libraryRemoved(self, library):
        self.libraries.remove(library)
        del self._libraryNames[library.name]
        self._sortedLibraries = None
        self.requestDeferredProcessing(self)
        
    def libraryChanged(self, library):
        self.requestDeferredProcessing(self)

    def makeLibraryFromPath(self, libraryPath, rootLib=None):
        (first, sep, rest) = libraryPath.partition('/')
        if libraryPath == '' or first == '..':
            return None
        if first == '' or first == '.':
            return self.makeLibraryFromPath(rest)
        if rootLib:
            lib = rootLib.libraryByPath(first)
            if not lib:
                lib = Library.createLibrary(first, self, rootLib)
        else:
            lib = self.libraryByPath(first)
            if not lib:
                lib = Library.createLibrary(first, self)
        if rest == '':
            return lib
        return self.makeLibraryFromPath(rest, lib)
        
    def libraryByPath(self, libraryPath):
        if libraryPath == '':
            return None
        (first, sep, rest) = libraryPath.partition('/')
        if first == '' or first == '.':
            return self.libraryByPath(rest)
        elif self.libraryNames.has_key(first):
            if rest == '':
                return self.libraryNames[first]
            else:
                return self.libraryNames[first].libraryByPath(rest)
        else:
            return None

    def cellByName(self, libraryPath, cellName):
        lib = self.libraryByPath(libraryPath)
        if lib:
            return lib.cellByName(cellName)
        else:
            return None

    def cellViewByName(self, libraryPath, cellName, cellViewName):
        lib = self.libraryByPath(libraryPath)
        if lib:
            return lib.cellViewByName(cellName, cellViewName)
        else:
            return None

    def runDeferredProcess(self):
        """
        Runs deferred processes of the Database class.
        Do not call it directly, Use Database.runDeferredProcesses(object)
        """
        self.updateDatabaseViews()
        
    def wasDeferredProcessingRequested(self, object=None):
        if object:
            return object in self._deferredProcessingObjects
        else:
            return len(self._deferredProcessingObjects) > 0
        
    def requestDeferredProcessing(self, object):
        """
        Request deferred processing of object's notifications.
        Once per object. No priorities or order guarantees.
        """
        self._deferredProcessingObjects.add(object)
        ##print self.__class__.__name__, "request", object
        self.client.deferredProcessingRequested()
        self.leaveCPU()
            
    def cancelDeferredProcessing(self, object):
        """
        Cancel deferred processing of a given object.
        For example, if it has already been triggered manually.
        """
        self._deferredProcessingObjects.remove(object)
        
    def runDeferredProcesses(self, object = None):
        """
        Force execution of all deferred processes.
        To be called synchronously or from within the main loop
        (an "idle" function).
        """
        if object:
            while self.wasDeferredProcessingRequested(object):
                self.cancelDeferredProcessing(object)
                o.runDeferredProcess()
        else:
            while self.wasDeferredProcessingRequested(object):
                dpos = list(self._deferredProcessingObjects)
                self._deferredProcessingObjects = set()
                for o in dpos:
                    ##print self.__class__.__name__, "run", o
                    o.runDeferredProcess()
            
    def leaveCPU(self):
        self.client.leaveCPU()
                
class Importer:
    def __init__(self, database):
        self._database = database
        self.reset()

    def reset(self):
        self._importedCellsView = set()
        self._reader = None
        self._fileList = []
        self._targetLibrary = 'work'
        self._overwrite = False
        self._recursive = True
