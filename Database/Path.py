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

from Exceptions import PathError

class Path():
    def __init__(self, pathName=None):
        if pathName:
            self._libraryPath = None
            self.cellName = None
            self.cellViewName = None
            self.absolute = False
            self.parse(pathName)
    
    @classmethod
    def createFromPathName(cls, pathName):
        self = cls(pathName)
        return self

    @classmethod
    def createFromNames(cls, pathName, cellName=None, cellViewName=None):
        self = cls()
        self._libraryPath = None
        self.cellName = cellName
        self.cellViewName = cellViewName
        self.absolute = False
        self.parseLibPath(pathName, pathName)
        if (cellViewName and cellViewName != '') and \
            (not cellName or cellName == ''):
            raise PathError(pathName + '//' + cellViewName, "Empty cell name")
        return self

    @classmethod
    def createFromPath(cls, path, idxStart=0, idxEnd=None):
        self = cls()
        self._origPath = path
        self._libraryPath = None
        self.cellName = path.cellName
        self.cellViewName = path.cellViewName
        self.absolute = path.absolute
        self._idxStart = idxStart
        self._idxEnd = idxEnd
        return self
        
    @property
    def name(self):
        s = ''
        if not self.absolute and self.subLibrary:
            for n in self.libraryPath:
                s += ('.' + str(n))
        elif not self.absolute:
            s += '.'
        else:
            s += str(self.libraryPath[0])
            for n in self.libraryPath[1:]:
                s += ('.' + str(n))
        if self.cellName:
            s += ('/' + str(self.cellName))
        if self.cellViewName:
            s += ('/' + str(self.cellViewName))
        return s

    @property
    def libraryPath(self):
        if self._libraryPath:
            return self._libraryPath
        else:
            lp = self._origPath.libraryPath[self._idxStart:self._idxEnd]
            return lp
        
    @property
    def libraryName(self):
        if len(self.libraryPath) > 0:
            return self.libraryPath[0]
        return ''

    @property
    def subLibrary(self):
        if len(self.libraryPath) > 0:
            return self.libraryPath[0]
        else:
            return None

    @property
    def descend(self):
        p = Path.createFromPath(self, 1)
        p.absolute = False
        return p
        
    @property
    def cell(self):
        p = Path.createFromPath(self)
        p.cellViewName=None
        return p
        
    @property
    def library(self):
        p = Path.createFromPath(self)
        p.cellViewName=None
        p.cellName=None
        return p
        
    @property
    def parentLibrary(self):
        if len(self.libraryPath) > 1:
            p = Path.createFromPath(self, 0, -1)
            p.cellViewName=None
            p.cellName=None
            return p
        raise PathError('', "Empty path name")
        
    def parse(self, name):
        if name == '':
            raise PathError(name, "Empty path name")
        (libPath, sep, rest) = name.partition('/')
        self.parseLibPath(libPath, name)
        if rest != '':
            (cellName, sep, rest2) = rest.partition('/')
            if cellName == '':
                raise PathError(name, "Empty cell name")
            self.cellName = cellName
            if rest2 != '':
                (cellViewName, sep, rest3) = rest2.partition('/')
                if cellViewName == '':
                    raise PathError(name, "Empty cell view name")
                if rest3 != '':
                    raise PathError(name, "Additional characters after the cell view name")
                self.cellViewName = cellViewName
        
    def parseLibPath(self, libPath, origName):
        if libPath == '':
            raise PathError(origName, "Unspecified library path name")
        (first, sep, rest) = libPath.partition('.')
        self.libraryPath = []
        if first != '':
            self.absolute = True
            self.libraryPath.append(first)
        else:
            self.absolute = False
            #self.libraryPath.append('.')
            if rest == '':
                return
        if sep != '':
            self.parseLibPathRec(rest, origName)

    def parseLibPathRec(self, libPath, origName):
        (first, sep, rest) = libPath.partition('.')
        if libPath == '' or first == '':
            raise PathError(origName, "Incorrect library path name")
        self.libraryPath.append(first)
        if sep != '':
            self.parseLibPathRec(rest, origName)

    def __repr__(self):
        return "Path('" + self.name + "')"
        