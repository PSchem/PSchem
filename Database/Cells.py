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

from CellViews import *
from Path import Path
from xml.etree import ElementTree as et

#print 'Cells out'

class Cell():

    @classmethod
    def createCell(cls, name, library):
        """Construct a Library object, or return an existing one."""
        if not Libraries.theLibraries:
            return
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
    def path(self):
        return self.library.path + '/' + self.name

    @property
    def library(self):
        return self._library
        
    @property
    def root(self):
        return self.library.root
        
    @property
    def database(self):
        return self.root.database

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

    def cellViewByPath(self, path, create=False):
        if self.cellViewNames.has_key(path.cellViewName):
            cellView = self.cellViewNames[path.cellViewName]
        #elif create:
        #    cellView = CellView.createCellView(path.cellViewName, self)
        else:
            return None
        return cellView
        
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
    def createLibrary(cls, name, parentLibrary = None):
        """Construct a Library object, or return an existing one."""
        if not Libraries.theLibraries:
            return
        if parentLibrary:
            parent = parentLibrary
        else:
            parent = Libraries.theLibraries
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
            return self.parentLibrary.path + '.' + self.name
        else:
            return self.name

    @property
    def parentLibrary(self):
        return self._parentLibrary

    @property
    def root(self):
        return Libraries.theLibraries
        
    @property
    def database(self):
        return self.root.database
        
    @property
    def sortedLibraries(self):
        """Cached list of libraries sorted by name."""
        if not self._sortedLibraries:
            self._sortedLibraries = sorted(self.libraries, lambda a, b: cmp(a.name.lower(), b.name.lower()))
        return self._sortedLibraries

    @property
    def sortedCells(self):
        """Cached list of cells sorted by name."""
        if not self._sortedCells:
            self._sortedCells = sorted(self.cells, lambda a, b: cmp(a.name.lower(), b.name.lower()))
        return self._sortedCells

    def cellAdded(self, cell):
        self.cells.add(cell)
        self.cellNames[cell.name] = cell
        self._sortedCells = None
        self.root.libraryChanged(self)

    def cellRemoved(self, cell):
        self.cells.remove(cell)
        del self.cellNames[cell.name]
        self._sortedCells = None
        self.root.libraryChanged(self)
        
    def cellChanged(self, cell):
        self.root.libraryChanged(self)

    def libraryAdded(self, library):
        self.libraries.add(library)
        self.libraryNames[library.name] = library
        self._sortedLibraries = None
        self.root.libraryChanged(self)

    def libraryRemoved(self, library):
        self.libraries.remove(library)
        del self.libraryNames[library.name]
        self._sortedLibraries = None
        self.root.libraryChanged(self)
        
    def libraryChanged(self, library):
        self.root.libraryChanged(self)

    def objectByPath__(self, libraryPath, create=False):
        (libraryPath, sep, cellPath) = path.partition('/')
        library = self.libraryByPath(libraryPath, create)
        if len(sep) == 0 or len(cellPath) == 0:
            return library
        elif library:
            return library.cellByPath(cellPath, create)
        else:
            return None
        
    def libraryByPath_(self, libraryPath, create=False):
        (libraryPath2, sep, rest) = libraryPath.partition('/') #remove cell/cellview if any
        (first, sep, rest) = libraryPath2.partition('.')
        if libraryPath2 == '':
            return None
        if len(sep) > 0 and libraryPath2 == '': #relative to itself
            self.libraryByPath(rest, create)
        if self.libraryNames.has_key(first):
            library = self.libraryNames[first]
        elif create:
            library = Library.createLibrary(first, self)
        else:
            return None
        if library and sep != '':
            return library.libraryByPath(rest, create)
        else:
            return library

    def cellByPath_(self, cellPath, create=False):
        (first, sep, rest) = cellPath.partition('/')
        if cellPath == '' or first == '':
            return None
        if self.cellNames.has_key(first):
            cell = self.cellNames[first]
        elif create:
            cell = Cell.createCell(first, self)
        else:
            return None
        if cell and sep != '':
            return cell.cellViewByPath(rest, create)
        else:
            return cell

    def objectByPath(self, path, create=False):
        if self.cellNames.has_key(path.cellName):
            cell = self.cellNames[path.cellName]
        elif create:
            cell = Cell.createCell(path.cellName, self)
        else:
            return None
        if cell and path.cellViewName:
            return cell.cellViewByPath(path, create)
        return cell

    def libraryByPath(self, path, create=False):
        if path.absolute:
            return self.libraries.libraryByPath(path, create)
        if not path.subLibrary:
            return self
        libName = path.libraryName
        if self.libraryNames.has_key(libName):
            library = self.libraryNames[libName]
        elif create:
            library = Library.createLibrary(libName, self)
        else:
            return
        return library.libraryByPath(path.descend, create)

    def createLibraryFromPath(self, path):
        return self.libraryByPath(path, True)
        
    def createCellFromPath(self, path):
        lib = self.createLibraryFromPath(path)
        return Cell.createCell(path.cellName, lib)
        
    def createSchematicFromPath(self, path):
        cell = self.createCellFromPath(path)
        return Schematic(self, cell)
        
    def createSymbolFromPath(self, path):
        cell = self.createCellFromPath(path)
        return Symbol(self, cell)
        
    #def libraryByPath(self, libraryPath):
    #    (first, sep, rest) = libraryPath.partition('.')
    #    if first == '':
    #        return None
    #    if first == '..':
    #        return self.parentLibrary.libraryByPath(rest)
    #    elif first == '.':
    #        return self.libraryByPath(rest)
    #    elif first == '':
    #        return self.database.libraryByPath(rest)
    #    elif self.libraryNames.has_key(first):
    #        if rest == '':
    #            return self.libraryNames[first]
    #        else:
    #            return self.libraryNames[first].libraryByPath(rest)
    #    else:
    #        return None

    #def cellByName(self, cellName):
    #    if self.cellNames.has_key(cellName):
    #        return self.cellNames[cellName]
    #    else:
    #        return None

    #def cellViewByName(self, cellName, cellViewName):
    #    cell = self.cellByName(cellName)
    #    if cell:
    #        return cell.cellViewByName(cellViewName)
    #    else:
    #        return None

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
            self.root.libraryRemoved(self)
        self.parentLibrary = None
        
class Libraries():
    theLibraries = None
    
    @classmethod
    def createLibraries(cls, database):
        """Construct a Libraries object, or return an existing one."""
        if Libraries.theLibraries:
            self = Libraries.theLibraries
        else:
            self = cls()
            Libraries.theLibraries = self
            self.database = database
            self._libraries = set()
            self._libraryNames = {}
            self._libraryViews = set()
            self._sortedLibraries = None
        return self
            
    @property
    def libraries(self):
        return self._libraries

    @property
    def libraryNames(self):
        return self._libraryNames

    @property
    def libraryViews(self):
        return self._libraryViews

    @property
    def sortedLibraries(self):
        """Cached list of libraries sorted by name."""
        if not self._sortedLibraries:
            self._sortedLibraries = sorted(self.libraries, lambda a, b: cmp(a.name.lower(), b.name.lower()))
        #print self._sortedLibraries
        return self._sortedLibraries

    def libraryViewAdded(self, view):
        self._libraryViews.add(view)

    def updateLibraryViews(self):
        "Notify views that the libraries layout has changed"
        for v in self._libraryViews:
            v.update()

    def updateLibraryViewsPreparation(self):
        """
        Some views may require notification before layout
        of the libraries changes
        """
        for v in self._libraryViews:
            v.prepareForUpdate()
        
    def libraryAdded(self, library):
        self.libraries.add(library)
        self.libraryNames[library.name] = library
        self._sortedLibraries = None
        self.database.requestDeferredProcessing(self)

    def libraryRemoved(self, library):
        self.libraries.remove(library)
        del self._libraryNames[library.name]
        self._sortedLibraries = None
        self.database.requestDeferredProcessing(self)
        
    def libraryChanged(self, library):
        self.database.requestDeferredProcessing(self)

    def objectByPath(self, path, create=False):
        library = self.libraryByPath(path, create)
        if library and path.cellName:
            return library.objectByPath(path, create)
        return library

    def libraryByPath(self, path, create=False):
        if not path.absolute or not path.subLibrary:
            return
        libName = path.libraryName
        if self.libraryNames.has_key(libName):
            library = self.libraryNames[libName]
        elif create:
            library = Library.createLibrary(libName)
        else:
            return
        return library.libraryByPath(path.descend, create)

    def createLibraryFromPath(self, path):
        return self.libraryByPath(path, True)
        
    def createCellFromPath(self, path):
        lib = self.createLibraryFromPath(path)
        return Cell.createCell(path.cellName, lib)
        
    def createSchematicFromPath(self, path):
        cell = self.createCellFromPath(path)
        return Schematic(self, cell)
        
    def createSymbolFromPath(self, path):
        cell = self.createCellFromPath(path)
        return Symbol(self, cell)
        
    def runDeferredProcess(self):
        """
        Runs deferred processes of the Database class.
        Do not call it directly, Use Database.runDeferredProcesses(object)
        """
        self.updateLibraryViews()
        
    def close(self):
        for l in list(self.libraries):
            pass
            #fix it
            #l.remove()
        Libraries.theLibraries = None
                
