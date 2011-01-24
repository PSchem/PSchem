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
from PSchem.Selection import *

class SelectMode():
    def __init__(self, view, transient=False):
        self._view = view
        self._optionPanel = None
        self._actions = set()
        self._mousePressedPos = None
        self._mousePressedButton = QtCore.Qt.NoButton
        self.installActions()
        self._lasso = None
        self._transient = transient

        self._optionPanel = SelectToolOptions()
        self._selection = Selection()
        self._toBeSelected = None
        self._preSelected = None
        self._modifiers = None
        self._pos = None
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(50)
        self._view.connect(self._timer, QtCore.SIGNAL("timeout()"), self.updatePreSelected)

    def setup(self, pos=None):
        self._pos = pos
        
    def view(self):
        return self._view

    def exitMode(self):
        if self._preSelected:
            self._preSelected.setPreSelected(False)
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
            scene = self._view.scene()
            scene.removeItem(self._lasso)
            scene.setSceneRect(scene.itemsBoundingRect())
            self._lasso = None

    def findItems(self, pos, modifiers=None):
        items = self._view.scene().items(pos)
        items = filter(lambda i: not(i.parentItem()), items)
        items = filter(lambda i: not(isinstance(i, Lasso)), items)
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
        if pos:
            self._mousePressedPos = pos

    def mouseReleaseEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
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

    def mouseMoveEvent(self, event, pos = None):
        if pos:
            self._pos = pos
            self._modifiers = event.modifiers()
            self._timer.start()

    def mouseDragEvent(self, event, pos = None):
        if pos and (event.buttons() & QtCore.Qt.LeftButton):
            #print "dragged", pos
            self.stretchLasso(pos)
        elif pos and (event.buttons() & QtCore.Qt.RightButton):
            mode = ZoomInMode(self._view, True)
            mode.setMousePressedPos(self._mousePressedPos)
            mode.mouseDragEvent(event, pos)
            self._view.modeStack.push(mode)

    def updatePreSelected(self):
        items = []
        #items = self.findItems(pos, event.modifiers())
        if self._pos:
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
            
    def name(self):
        return "Select"


class ZoomInMode(SelectMode):
    def __init__(self, view, transient=False):
        SelectMode.__init__(self, view, transient)

    def mousePressEvent(self, event, pos = None):
        if pos: # and event.button() == QtCore.Qt.LeftButton:
            self._mousePressedPos = pos
        else:
            SelectMode.mousePressEvent(self, event, pos)

    def mouseReleaseEvent(self, event, pos = None):
        if pos: # and event.button() == QtCore.Qt.LeftButton:
            if self.lassoRect():
                lassoRect = self.lassoRect()
                self.removeLasso()
                self._view.fitRect(lassoRect)
            if self.transient():
                self._view.modeStack.popMode()
        else:
            SelectMode.mouseReleaseEvent(self, event, pos)

    def mouseDragEvent(self, event, pos = None):
        if pos: # and (event.buttons() & QtCore.Qt.LeftButton):
            self.stretchLasso(pos)
        else:
            SelectMode.mouseDragEvent(self, event, pos)

    def name(self):
        return "Zoom In"

class MoveMode(SelectMode):
    def __init__(self, view, transient=False):
        SelectMode.__init__(self, view, transient)

    def setup(self, pos=None):
        if pos:
            self._refPoint = pos
        else:
            self.selectRefPoint()
        
    def selectRefPoint(self):
        print "Select a Ref Point"
        self._selectRefPoint = True
        
    def selectDest(self):
        print "Select Destination"
        self._selectRefPoint = False

    def refPoint(self):
        return self._refPoint
        
    def mousePressEvent(self, event, pos = None):
        if pos: # and event.button() == QtCore.Qt.LeftButton:
            self._mousePressedPos = pos

    def mouseReleaseEvent(self, event, pos = None):
        if pos: # and event.button() == QtCore.Qt.LeftButton:
            if self._selectRefPoint:
                self._refPoint = pos
                print "x: "+str(pos.x())+",\t y: "+str(pos.y())
                self.selectDest()
            else:
                print "x: "+str(pos.x())+",\t y: "+str(pos.y())
                if self.transient():
                    self._view.modeStack.popMode()
                else:
                    self.selectRefPoint()

    def mouseDragEvent(self, event, pos = None):
        pass

    def mouseMoveEvent(self, event, pos = None):
        pass

    def name(self):
        return "Move"

class RefPointMode(SelectMode):
    def __init__(self, view, transient=True):
        SelectMode.__init__(self, view, transient)
        self._refPoint = None
        
    def mouseReleaseEvent(self, event, pos = None):
        if pos and event.button() == QtCore.Qt.LeftButton:
            self._refPoint = pos
            if self.transient():
                self._view.modeStack.popMode()
        else:
            SelectMode.mouseReleaseEvent(self, event, pos)

    def refPoint(self):
        return self._refPoint
        
    def name(self):
        return "Select Ref Point"
            
class ModeStack(list):
    def __init__(self, view):
        list.__init__(self)
        self._view = view
        self.append(SelectMode(view))

    def isEmpty(self):
        return len(self) <= 1

    def push(self, mode):
        #self.top().exitMode()
        if mode.name() != self.top().name():
            self.append(mode)
            print "In a " + mode.name() + " mode"
            mode.setup()

    def pushSelectMode(self):
        self.push(SelectMode(self._view))

    def pushZoomInMode(self):
        self.push(ZoomInMode(self._view, True))

    def pushMoveMode(self):
        self.push(MoveMode(self._view, True))

    def popMode(self):
        if not self.isEmpty():
            mode = self.pop()
            mode.exitMode()
            print "In a " + self.top().name() + " mode"
            return mode
        else:
            return None

    def top(self):
        #print len(self)-1
        return self[len(self)-1]
