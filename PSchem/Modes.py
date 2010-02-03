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
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

from PSchem.ToolOptions import *
from PSchem.Lasso import *

class Mode():
    def __init__(self, view, transient=False):
        self._view = view
        self._optionPanel = None
        self._actions = set()
        self._mousePressedPos = None
        self._mousePressedButton = QtCore.Qt.NoButton
        self.installActions()
        self._lasso = None
        self._transient = transient

    def view(self):
        return self._view

    def exitMode(self):
        self.removeLasso()
        self.uninstallActions()

    def installActions(self):
        for a in self.actions():
            self._view.addAction(a)

    def uninstallActions(self):
        for a in self.actions():
            self._view.removeAction(a)

    def actions(self):
        return self._actions

    def transient(self):
        return self._transient

    def setMousePressedPos(self, pos):
        self._mousePressedPos = pos
    
    def mousePressedPos(self):
        return self._mousePressedPos
    
    def mousePressEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.RightButton:
            #print self._mousePressedPos
            self._mousePressedPos = pos

    def mouseReleaseEvent(self, event, pos = None):
        pass

    def mouseMoveEvent(self, event, pos = None):
        pass

    def mouseDragEvent(self, event, pos = None):
        if pos and (event.buttons() & QtCore.Qt.RightButton):
            mode = ZoomInMode(self._view, True)
            mode.setMousePressedPos(self._mousePressedPos)
            mode.mouseDragEvent(event, pos)
            self._view.modeStack.push(mode)
            
    def addLasso(self, pos):
        self._lasso = Lasso(self._view, pos)
        self._view.scene().addItem(self._lasso)
        
    def stretchLasso(self, pos):
        if not self._lasso:
            self.addLasso(self._mousePressedPos)
        self._lasso.stretchTo(pos)
    
    def lassoRect(self):
        return self._lasso and self._lasso.rect()
    
    def removeLasso(self):
        if self._lasso:
            self._view.scene().removeItem(self._lasso)
            self._lasso = None
    
    def name(self):
        return "Abstract"
        
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
            i.setSelected(True)
            i.update()

    def add(self, item):
        set.add(self, item)
        item.setSelected(True)
        item.update()
        
    def remove(self, item):
        set.remove(self, item)
        item.setSelected(False)
        item.update()
        
    def __ior__(self, items):
        set.__ior__(self, items)
        for i in items:
            i.setSelected(True)
            i.update()
        return self

    def __isub__(self, items):
        set.__isub__(self, items)
        for i in items:
            i.setSelected(False)
            i.update()
        return self

    def __del__(self):
        for i in self:
            i.setSelected(False)
            i.update()

class SelectMode(Mode):
    def __init__(self, view, transient=False):
        Mode.__init__(self, view, transient)
        self._optionPanel = SelectToolOptions()
        self._selection = Selection()
        self._toBeSelected = None
        self._preSelected = None
        self._modifiers = None
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(50)
        self._view.connect(self._timer, QtCore.SIGNAL("timeout()"), self.updatePreSelected)

    def findItems(self, pos, modifiers=None):
        items = self._view.scene().items(pos)
        items = filter(lambda i: not(i.parentItem()), items)
        #items = map(lambda i: i.model, items)
        items = set(items)
        if self.addMode(modifiers):
            return ItemBuffer(items - self._selection, pos)
        elif self.subtractMode(modifiers):
            return ItemBuffer(items & self._selection, pos)
        else:
            itemsBuf = ItemBuffer(items, pos)
            itemsBuf.setPointerToUnique(self._selection)
            #print '->' + str(self._selection)
            #print '->' + str(itemsBuf) + str(itemsBuf.pointer())
            return itemsBuf
            
    def currentItem(self):
        item = None
        if self._toBeSelected:
            item = self._toBeSelected.current()
        return item

    def nextItem(self):
        if self._toBeSelected:
            self._toBeSelected.next()

    def addMode(self, modifiers):
        return modifiers & QtCore.Qt.ShiftModifier
            
    def subtractMode(self, modifiers):
        return modifiers & QtCore.Qt.ControlModifier
            
    def mousePressEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            self._modifiers = event.modifiers()
            self._mousePressedPos = pos
        else:
            Mode.mousePressEvent(self, event, pos)

    def mouseReleaseEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            self._modifiers = event.modifiers()
            #print "released", pos
            if self.lassoRect():
                items = self._view.scene().items(self.lassoRect(), QtCore.Qt.ContainsItemShape)
                items = filter(lambda i: not(i.parentItem()), items)
                #items = map(lambda i: i.model, items)
                if self.addMode(event.modifiers()):
                    self._selection |= items
                elif self.subtractMode(event.modifiers()):
                    self._selection -= items
                else:
                    self._selection = Selection(items)
                self._toBeSelected = None
                self.removeLasso()
                self.updatePreSelected()
            else:
                if not self._toBeSelected or self._toBeSelected.pos() != pos:
                    self._toBeSelected = self.findItems(pos, event.modifiers())
                item = self.currentItem()
                if not self.addMode(event.modifiers()) and not self.subtractMode(event.modifiers()):
                    self._selection = None
                    self._selection = Selection()
                if item:
                    if self.subtractMode(event.modifiers()):
                        self._selection.remove(item)
                    else:
                        self._selection.add(item)
                self.nextItem()
                item = self.currentItem()
                self.updatePreSelected()
        else:
            Mode.mouseReleaseEvent(self, event, pos)

    def updatePreSelected(self):
        #items = self.findItems(pos, event.modifiers())
        items = self.findItems(self._pos, self._modifiers)
        #item = self.currentItem()
        item = None
        if len(items) > 0:
            item = items[0]
        #print item, self._preSelected
        
        if item != self._preSelected:
            if self._preSelected:
                self._preSelected.setPreSelected(False)
                self._preSelected.update()
            if item:
                self._preSelected = item
                item.setPreSelected(True)
                item.update()
            
    def mouseMoveEvent(self, event, pos = None):
        if pos:
            self._pos = pos
            self._modifiers = event.modifiers()
            self._timer.start()
        else:
            Mode.mouseMoveEvent(self, event, pos)

    def mouseDragEvent(self, event, pos = None):
        if pos and (event.buttons() & QtCore.Qt.LeftButton):
            self._modifiers = event.modifiers()
            #print "dragged", pos

            self.stretchLasso(pos)
        else:
            Mode.mouseDragEvent(self, event, pos)

    def name(self):
        return "Select"


class ZoomInMode(Mode):
    def __init__(self, view, transient=False):
        Mode.__init__(self, view, transient)
        #print "Select the area to zoom in"
        self._prevCursor = self.view().cursor()
        #self.view().setCursor(QtCore.Qt.PointingHandCursor)

    def mousePressEvent(self, event, pos = None):
        #if pos and event.button() == QtCore.Qt.LeftButton:
            self.addLasso(pos)
        #else:
        #    Mode.mousePressEvent(self, event, pos)

    def mouseReleaseEvent(self, event, pos = None):
        #if pos and event.button() == QtCore.Qt.LeftButton:
            if self.lassoRect():
                self._view.fitRect(self.lassoRect())
                self.removeLasso()
            if self.transient():
                self._view.modeStack.popMode()
        #else:
        #    Mode.mouseReleaseEvent(self, event, pos)

    def mouseDragEvent(self, event, pos = None):
        #if pos and (event.buttons() & QtCore.Qt.LeftButton):
            self.stretchLasso(pos)
        #else:
        #    Mode.mouseDragEvent(self, event, pos)

    def name(self):
        return "Zoom In"

class ModeStack(list):
    def __init__(self, view):
        list.__init__(self)
        self._view = view
        self.push(SelectMode(view))

    def isEmpty(self):
        return len(self) <= 1

    def push(self, mode):
        self.append(mode)
        print "In \"" + mode.name() + "\" mode"

    def pushSelectMode(self):
        self.push(SelectMode(self._view))

    def pushZoomInMode(self):
        self.push(ZoomInMode(self._view))

    def popMode(self):
        if not self.isEmpty():
            mode = self.pop()
            mode.exitMode()
            print "In \"" + self.top().name() + "\" mode"
            return mode
        else:
            return None

    def top(self):
        #print len(self)-1
        return self[len(self)-1]
