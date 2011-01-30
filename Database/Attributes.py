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

#from Database.Cells import *
from xml.etree import ElementTree as et

class Attribute():
    AString   = 'string'
    AInteger   = 'int'
    AFloat   = 'float'

    def __init__(self, name, val, type, parent):
        self._name = name
        self._val = val
        self._type = type
        self._editable = True

        self._parent = parent
        
    def setName(self, name):
        if self._editable:
            self._name = name
            self._parent.updateViews()

    def setVal(self, val):
        if self._editable:
            self._val = val
            self._parent.updateViews()

    def setType(self, type):
        if self._editable:
            self._type = type
            self._parent.updateViews()

    def setEditable(self, editable):
        self._editable = editable
        self._parent.updateViews()

    def parent(self):
        return self._parent

    def name(self):
        return self._name

    def val(self):
        return self._val

    def type(self):
        return self._type

    def editable(self):
        return self._editable
        
    def toXml(self):
        elem = et.Element(self._name)
        elem.attrib['type'] = str(self._type)
        elem.text = str(self._val)
        return elem

