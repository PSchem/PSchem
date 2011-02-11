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

#from Cells import *
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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if self._editable:
            self._name = name
            self._parent.updateViews()

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        if self._editable:
            self._val = val
            self._parent.updateViews()

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        if self._editable:
            self._type = type
            self._parent.updateViews()

    @property
    def editable(self):
        return self._editable
        
    @editable.setter
    def editable(self, editable):
        self._editable = editable
        self._parent.updateViews()
        
    @property
    def parent(self):
        return self._parent

    def toXml(self):
        elem = et.Element(self._name)
        elem.attrib['type'] = str(self._type)
        elem.text = str(self._val)
        return elem

