# -*- coding: utf-8 -*-

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
import sys
import math

class Command():
    #pstrip = re.compile(r'\n$')
    def __init__(self, commandStr, type = 'single'):
        self._text = commandStr
        self._type = type
        self._compiled = None
        
    def compiled(self):
        if (not self._compiled):
            self._compiled = compile(self._text, "console", self._type)
        return self._compiled
        
    def text(self):
        #text = Controller.pstrip.sub('', self._str)
        return self._text

class Controller():

    def __init__(self, window):
        self.window = window
        currentView = window.currentView
        currentCellView = window.currentCellView
        database = window.database
        self.locals = locals()
        self.globals = globals()
        

    def execute(self, cmd, echo = True):
        if echo:
            sys.stdout.write('--- ' + cmd.text() + '\n')
        exec (cmd.compiled(), self.globals, self.locals)

                
