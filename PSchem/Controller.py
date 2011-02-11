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

import re
#from PSchem.ConsoleWidget import *
from Database.Cells import *
from Database.CellViews import *
from Database.Primitives import *
from Database.Design import *
from Database.Attributes import *
from Database.Layers import *
from Database.Path import *
from Database.Exceptions import *
import traceback
import sys
import math
from PyQt4 import QtGui, QtCore

class Controller():

    def __init__(self, wnd):
        global window
        window = wnd
        self.window = window
        global currentView
        currentView = window.currentView
        global currentCellView
        currentCellView = window.currentCellView
        global database
        database = window.database
        self.locals = locals()
        self.globals = globals()
        

    def execute(self, cmd, echo = True):
        if echo:
            sys.stdout.pushSync(False)
            sys.stdout.write('--- ' + cmd.text() + '\n')
            try:
                exec (cmd.compiled(), self.globals, self.locals)
            except DatabaseError:
                traceback.print_exc()
            #if res is not None:
            #    sys.stdout.write('=== '+str(res))
            sys.stdout.popSync()
        else:
            sys.stdout.pushSync(True)
            #sys.stdout.write('=== ')
            #exec (cmd.compiled(), self.globals, self.locals)
            try:
                exec (cmd.compiled(), self.globals, self.globals)
            except DatabaseError:
                traceback.print_exc()
            #if res is not None:
            #    sys.stdout.write('=== '+str(res))
            sys.stdout.popSync()

