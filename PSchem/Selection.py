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

#import Globals
#Qt = __import__(Globals.UI,  globals(),  locals(),  ['QtCore',  'QtGui'])
#QtCore = Qt.QtCore
#QtGui = Qt.QtGui

#from PyQt4 import QtCore, QtGui

class ItemBuffer(list):
    def __init__(self, items, pos=None):
        list.__init__(self, items)
        #print self
        self._pos = pos
        self._pointer = 0

    def current(self):
        if self._pointer < len(self):
            return self[self._pointer]
        else:
            return None

    def pointer(self):
        return self._pointer

    def setPointer(self, pointer):
        #print 'pos', pos
        if pointer < 0 or len(self) == 0:
            self._pointer = 0
            return
        if pointer < len(self):
            self._pointer = pointer
        else:
            self.setPointer(pointer - len(self))

    def setPointerToUnique(self, coll):
        j = 0
        for i in range(0, len(self)):
            #print str(i) + str(self[i]) + str(self[i] in coll)
            if not self[i] in coll:
                break
            j = j + 1
        self.setPointer(j)
        
    def next(self):
        self.setPointer(self._pointer + 1)
    
    def pos(self):
        return self._pos

class Selection(set):
    def __init__(self, items=[]):
        set.__init__(self, items)
        for i in items:
            i.selected = True
            i.update()
        if len(items) > 0:
            print self.__class__.__name__, self

    def add(self, item):
        set.add(self, item)
        item.selected = True
        item.update()
        print self.__class__.__name__, self
        
    def remove(self, item):
        set.remove(self, item)
        item.selected = False
        item.update()
        print self.__class__.__name__, self
        
    def __ior__(self, items):
        set.__ior__(self, items)
        for i in items:
            i.selected = True
            i.update()
        print self.__class__.__name__, self
        return self

    def __isub__(self, items):
        set.__isub__(self, items)
        for i in items:
            i.selected = False
            i.update()
        print self.__class__.__name__, self
        return self

    def __del__(self):
        for i in self:
            i.selected = False
            i.update()
        #print self.__class__.__name__, self

